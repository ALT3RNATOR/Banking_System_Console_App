import os
import datetime
import random
import hashlib
import time

class Account:
    def __init__(self, account_number, name, password, balance):
        self.account_number = account_number
        self.name = name
        self.password = password  # Should be stored as a hash in real applications
        self.balance = float(balance)

    def deposit(self, amount):
        if amount <= 0:
            return False, "Amount must be positive."
        
        self.balance += amount
        return True, f"Deposit successful! Current balance: {self.balance}"

    def withdraw(self, amount):
        if amount <= 0:
            return False, "Amount must be positive."
        
        if amount > self.balance:
            return False, "Insufficient funds."
        
        self.balance -= amount
        return True, f"Withdrawal successful! Current balance: {self.balance}"
    
    def get_balance(self):
        return self.balance

class BankingSystem:
    def __init__(self):
        self.accounts_file = "accounts.txt"
        self.transactions_file = "transactions.txt"
        self.ensure_files_exist()
        self.current_account = None
    
    def ensure_files_exist(self):
        """Create files if they don't exist"""
        if not os.path.exists(self.accounts_file):
            with open(self.accounts_file, "w") as f:
                f.write("")  # Create an empty file
                
        if not os.path.exists(self.transactions_file):
            with open(self.transactions_file, "w") as f:
                f.write("")  # Create an empty file
    
    def hash_password(self, password):
        """Simple password hashing using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_account_number(self):
        """Generate a unique 6-digit account number"""
        while True:
            account_number = str(random.randint(100000, 999999))
            if not self.account_exists(account_number):
                return account_number
    
    def account_exists(self, account_number):
        """Check if an account number already exists"""
        with open(self.accounts_file, "r") as f:
            for line in f:
                if line.strip():
                    acc_num = line.split(",")[0]
                    if acc_num == account_number:
                        return True
        return False
    
    def get_account(self, account_number):
        """Retrieve account details by account number"""
        with open(self.accounts_file, "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(",")
                    if parts[0] == account_number:
                        return Account(parts[0], parts[1], parts[2], parts[3])
        return None
    
    def create_account(self, name, initial_deposit, password):
        """Create a new bank account"""
        if initial_deposit <= 0:
            return False, "Initial deposit must be positive."
        
        account_number = self.generate_account_number()
        hashed_password = self.hash_password(password)
        
        # Save account to file
        with open(self.accounts_file, "a") as f:
            f.write(f"{account_number},{name},{hashed_password},{initial_deposit}\n")
        
        # Log the initial deposit as a transaction
        self.log_transaction(account_number, "Deposit", initial_deposit)
        
        return True, account_number
    
    def login(self, account_number, password):
        """Authenticate a user"""
        account = self.get_account(account_number)
        if not account:
            return False, "Account not found."
        
        hashed_password = self.hash_password(password)
        if account.password != hashed_password:
            return False, "Incorrect password."
        
        self.current_account = account
        return True, "Login successful!"
    
    def logout(self):
        """Log out the current user"""
        self.current_account = None
    
    def deposit(self, amount):
        """Deposit money into the current account"""
        if not self.current_account:
            return False, "No account logged in."
        
        success, message = self.current_account.deposit(amount)
        if success:
            self.update_account_balance()
            self.log_transaction(self.current_account.account_number, "Deposit", amount)
        
        return success, message
    
    def withdraw(self, amount):
        """Withdraw money from the current account"""
        if not self.current_account:
            return False, "No account logged in."
        
        success, message = self.current_account.withdraw(amount)
        if success:
            self.update_account_balance()
            self.log_transaction(self.current_account.account_number, "Withdrawal", amount)
        
        return success, message
    
    def update_account_balance(self):
        """Update the account balance in the file"""
        accounts = []
        
        # Read all accounts
        with open(self.accounts_file, "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(",")
                    if parts[0] == self.current_account.account_number:
                        parts[3] = str(self.current_account.balance)
                    accounts.append(",".join(parts))
        
        # Write back all accounts with updated balance
        with open(self.accounts_file, "w") as f:
            for account in accounts:
                f.write(f"{account}\n")
    
    def log_transaction(self, account_number, transaction_type, amount):
        """Log a transaction to the transactions file"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        with open(self.transactions_file, "a") as f:
            f.write(f"{account_number},{transaction_type},{amount},{today}\n")
    
    def get_transaction_history(self):
        """Get transaction history for the current account"""
        if not self.current_account:
            return []
        
        transactions = []
        with open(self.transactions_file, "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(",")
                    if parts[0] == self.current_account.account_number:
                        transactions.append({
                            "type": parts[1],
                            "amount": float(parts[2]),
                            "date": parts[3]
                        })
        
        return transactions


def main():
    bank = BankingSystem()
    
    while True:
        clear_screen()
        print("\n===== Banking System =====")
        
        if bank.current_account:
            logged_in_menu(bank)
        else:
            main_menu(bank)

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu(bank):
    """Display the main menu for logged-out users"""
    print("1. Create Account")
    print("2. Login")
    print("3. Exit")
    
    choice = input("\nEnter your choice: ")
    
    if choice == "1":
        create_account_menu(bank)
    elif choice == "2":
        login_menu(bank)
    elif choice == "3":
        print("Thank you for using the Banking System!")
        exit()
    else:
        print("Invalid choice. Please try again.")
        time.sleep(1)

def create_account_menu(bank):
    """Handle the account creation process"""
    clear_screen()
    print("\n===== Create New Account =====")
    
    name = input("Enter your name: ")
    while True:
        try:
            initial_deposit = float(input("Enter your initial deposit: "))
            if initial_deposit <= 0:
                print("Initial deposit must be positive.")
                continue
            break
        except ValueError:
            print("Please enter a valid amount.")
    
    password = input("Enter a password: ")
    
    # Create the account
    success, result = bank.create_account(name, initial_deposit, password)
    
    if success:
        print(f"\nAccount created successfully!")
        print(f"Your account number: {result}")
        print("Please save this number for login.")
    else:
        print(f"\nError: {result}")
    
    input("\nPress Enter to continue...")

def login_menu(bank):
    """Handle the login process"""
    clear_screen()
    print("\n===== Login =====")
    
    account_number = input("Enter your account number: ")
    password = input("Enter your password: ")
    
    success, message = bank.login(account_number, password)
    
    print(f"\n{message}")
    if not success:
        input("\nPress Enter to continue...")

def logged_in_menu(bank):
    """Display the menu for logged-in users"""
    account = bank.current_account
    print(f"Welcome, {account.name}!")
    print(f"Account Number: {account.account_number}")
    print(f"Current Balance: ${account.balance:.2f}")
    print("\n1. Deposit")
    print("2. Withdraw")
    print("3. View Transaction History")
    print("4. Logout")
    
    choice = input("\nEnter your choice: ")
    
    if choice == "1":
        deposit_menu(bank)
    elif choice == "2":
        withdraw_menu(bank)
    elif choice == "3":
        view_transactions(bank)
    elif choice == "4":
        bank.logout()
        print("Logged out successfully.")
        time.sleep(1)
    else:
        print("Invalid choice. Please try again.")
        time.sleep(1)

def deposit_menu(bank):
    """Handle deposit process"""
    clear_screen()
    print("\n===== Deposit =====")
    
    try:
        amount = float(input("Enter amount to deposit: $"))
        success, message = bank.deposit(amount)
        print(f"\n{message}")
    except ValueError:
        print("\nPlease enter a valid amount.")
    
    input("\nPress Enter to continue...")

def withdraw_menu(bank):
    """Handle withdrawal process"""
    clear_screen()
    print("\n===== Withdraw =====")
    
    try:
        amount = float(input("Enter amount to withdraw: $"))
        success, message = bank.withdraw(amount)
        print(f"\n{message}")
    except ValueError:
        print("\nPlease enter a valid amount.")
    
    input("\nPress Enter to continue...")

def view_transactions(bank):
    """Display transaction history"""
    clear_screen()
    print("\n===== Transaction History =====")
    
    transactions = bank.get_transaction_history()
    
    if not transactions:
        print("No transactions found.")
    else:
        for i, transaction in enumerate(transactions, 1):
            print(f"{i}. {transaction['type']}: ${transaction['amount']:.2f} on {transaction['date']}")
    
    input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()