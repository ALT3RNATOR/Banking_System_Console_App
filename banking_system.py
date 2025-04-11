import os
import datetime
import random
import hashlib
import time
import sys
from getpass import getpass

# ANSI color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
        return True, f"Deposit successful! Current balance: ${self.balance:.2f}"

    def withdraw(self, amount):
        if amount <= 0:
            return False, "Amount must be positive."
        
        if amount > self.balance:
            return False, "Insufficient funds."
        
        self.balance -= amount
        return True, f"Withdrawal successful! Current balance: ${self.balance:.2f}"
    
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
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                        # The date might have a space in it, so join all parts after the amount
                        date_parts = parts[3:]
                        date = ",".join(date_parts)
                        transactions.append({
                            "type": parts[1],
                            "amount": float(parts[2]),
                            "date": date
                        })
        
        # Sort transactions by date (newest first)
        transactions.reverse()
        return transactions


def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_loading_animation(text="Loading", duration=1.5):
    """Display a loading animation"""
    animation = "|/-\\"
    idx = 0
    end_time = time.time() + duration
    
    print("")
    while time.time() < end_time:
        print(f"\r{text} {animation[idx % len(animation)]}", end="")
        idx += 1
        time.sleep(0.1)
    print("\r" + " " * (len(text) + 2))  # Clear the line

def print_header(text):
    """Print a styled header"""
    width = 50
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'═' * width}")
    print(f"{text.center(width)}")
    print(f"{'═' * width}{Colors.ENDC}")

def print_success(text):
    """Print a success message"""
    print(f"{Colors.GREEN}{text}{Colors.ENDC}")

def print_error(text):
    """Print an error message"""
    print(f"{Colors.FAIL}{text}{Colors.ENDC}")

def print_info(text):
    """Print an info message"""
    print(f"{Colors.CYAN}{text}{Colors.ENDC}")

def print_warning(text):
    """Print a warning message"""
    print(f"{Colors.WARNING}{text}{Colors.ENDC}")

def print_menu_option(number, text):
    """Print a menu option"""
    print(f"{Colors.BLUE}[{number}] {Colors.ENDC}{text}")

def print_balance(balance):
    """Print the balance with color based on amount"""
    if balance > 1000:
        color = Colors.GREEN
    elif balance > 0:
        color = Colors.BLUE
    else:
        color = Colors.WARNING
    
    print(f"Current Balance: {color}${balance:.2f}{Colors.ENDC}")

def show_welcome_screen():
    """Display an attractive welcome screen"""
    clear_screen()
    print("\n" + "═" * 60)
    print(f"{Colors.BOLD}{Colors.CYAN}" + """
     ██████╗  █████╗ ███╗   ██╗██╗  ██╗██╗███╗   ██╗ ██████╗ 
     ██╔══██╗██╔══██╗████╗  ██║██║ ██╔╝██║████╗  ██║██╔════╝ 
     ██████╔╝███████║██╔██╗ ██║█████╔╝ ██║██╔██╗ ██║██║  ███╗
     ██╔══██╗██╔══██║██║╚██╗██║██╔═██╗ ██║██║╚██╗██║██║   ██║
     ██████╔╝██║  ██║██║ ╚████║██║  ██╗██║██║ ╚████║╚██████╔╝
     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
                                                             
          ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗
          ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║
          ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║
          ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║
          ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║
          ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝
    """ + f"{Colors.ENDC}")
    print(" " * 15 + f"{Colors.BOLD}Your Secure Banking Solution{Colors.ENDC}")
    print("═" * 60 + "\n")
    time.sleep(2)

def type_effect(text, delay=0.03):
    """Create a typing effect for text"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def main():
    bank = BankingSystem()
    show_welcome_screen()
    
    while True:
        clear_screen()
        if bank.current_account:
            logged_in_menu(bank)
        else:
            main_menu(bank)

def main_menu(bank):
    """Display the main menu for logged-out users"""
    print_header("MAIN MENU")
    print_menu_option(1, "Create Account")
    print_menu_option(2, "Login")
    print_menu_option(3, "Exit")
    
    choice = input(f"\n{Colors.BOLD}Enter your choice: {Colors.ENDC}")
    
    if choice == "1":
        create_account_menu(bank)
    elif choice == "2":
        login_menu(bank)
    elif choice == "3":
        clear_screen()
        type_effect(f"{Colors.GREEN}Thank you for using our Banking System! Goodbye!{Colors.ENDC}")
        time.sleep(1.5)
        exit()
    else:
        print_error("Invalid choice. Please try again.")
        time.sleep(1)

def create_account_menu(bank):
    """Handle the account creation process"""
    clear_screen()
    print_header("CREATE NEW ACCOUNT")
    
    name = input(f"{Colors.CYAN}Enter your name: {Colors.ENDC}")
    
    while True:
        try:
            initial_deposit = float(input(f"{Colors.CYAN}Enter your initial deposit ($): {Colors.ENDC}"))
            if initial_deposit <= 0:
                print_error("Initial deposit must be positive.")
                continue
            break
        except ValueError:
            print_error("Please enter a valid amount.")
    
    # Use getpass for password input if available, otherwise fall back to regular input
    try:
        password = getpass(f"{Colors.CYAN}Create a password: {Colors.ENDC}")
        confirm_password = getpass(f"{Colors.CYAN}Confirm password: {Colors.ENDC}")
    except:
        print_warning("Secure password entry not available. Password will be visible.")
        password = input(f"{Colors.CYAN}Create a password: {Colors.ENDC}")
        confirm_password = input(f"{Colors.CYAN}Confirm password: {Colors.ENDC}")
    
    if password != confirm_password:
        print_error("Passwords don't match!")
        input(f"\n{Colors.BOLD}Press Enter to try again...{Colors.ENDC}")
        return
    
    # Create the account with animation
    print_loading_animation("Creating your account", 1.5)
    
    success, result = bank.create_account(name, initial_deposit, password)
    
    if success:
        print_success("\n✓ Account created successfully!")
        print_info(f"Your account number: {Colors.BOLD}{result}{Colors.ENDC}")
        print_warning("Please save this number for login.")
    else:
        print_error(f"Error: {result}")
    
    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")

def login_menu(bank):
    """Handle the login process"""
    clear_screen()
    print_header("LOGIN")
    
    account_number = input(f"{Colors.CYAN}Enter your account number: {Colors.ENDC}")
    
    # Use getpass for password input if available
    try:
        password = getpass(f"{Colors.CYAN}Enter your password: {Colors.ENDC}")
    except:
        password = input(f"{Colors.CYAN}Enter your password: {Colors.ENDC}")
    
    print_loading_animation("Authenticating", 1)
    
    success, message = bank.login(account_number, password)
    
    if success:
        print_success(f"\n✓ {message}")
        time.sleep(1)
    else:
        print_error(f"\n✗ {message}")
        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")

def logged_in_menu(bank):
    """Display the menu for logged-in users"""
    account = bank.current_account
    
    print_header(f"WELCOME, {account.name.upper()}!")
    print_info(f"Account Number: {account.account_number}")
    print_balance(account.balance)
    
    print("\n" + "─" * 50)
    print_menu_option(1, "Deposit Funds")
    print_menu_option(2, "Withdraw Funds")
    print_menu_option(3, "View Transaction History")
    print_menu_option(4, "Logout")
    print("─" * 50)
    
    choice = input(f"\n{Colors.BOLD}Enter your choice: {Colors.ENDC}")
    
    if choice == "1":
        deposit_menu(bank)
    elif choice == "2":
        withdraw_menu(bank)
    elif choice == "3":
        view_transactions(bank)
    elif choice == "4":
        print_loading_animation("Logging out", 1)
        bank.logout()
        print_success("Logged out successfully!")
        time.sleep(1)
    else:
        print_error("Invalid choice. Please try again.")
        time.sleep(1)

def deposit_menu(bank):
    """Handle deposit process"""
    clear_screen()
    print_header("DEPOSIT FUNDS")
    
    try:
        amount = float(input(f"{Colors.CYAN}Enter amount to deposit ($): {Colors.ENDC}"))
        
        print_loading_animation("Processing deposit", 1.5)
        
        success, message = bank.deposit(amount)
        
        if success:
            print_success(f"\n✓ {message}")
        else:
            print_error(f"\n✗ {message}")
    except ValueError:
        print_error("\nPlease enter a valid amount.")
    
    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")

def withdraw_menu(bank):
    """Handle withdrawal process"""
    clear_screen()
    print_header("WITHDRAW FUNDS")
    
    try:
        amount = float(input(f"{Colors.CYAN}Enter amount to withdraw ($): {Colors.ENDC}"))
        
        print_loading_animation("Processing withdrawal", 1.5)
        
        success, message = bank.withdraw(amount)
        
        if success:
            print_success(f"\n✓ {message}")
            # ASCII art receipt
            print("\n" + "─" * 35)
            print("         WITHDRAWAL RECEIPT         ")
            print("─" * 35)
            print(f" Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f" Account: {bank.current_account.account_number}")
            print(f" Amount: ${amount:.2f}")
            print(f" Remaining: ${bank.current_account.balance:.2f}")
            print("─" * 35)
            print("      Thank you for banking with us!      ")
            print("─" * 35)
        else:
            print_error(f"\n✗ {message}")
    except ValueError:
        print_error("\nPlease enter a valid amount.")
    
    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")

def view_transactions(bank):
    """Display transaction history"""
    clear_screen()
    print_header("TRANSACTION HISTORY")
    
    print_loading_animation("Fetching transactions", 1.5)
    
    transactions = bank.get_transaction_history()
    
    if not transactions:
        print_warning("No transactions found.")
    else:
        print("\n" + "─" * 60)
        print(f"{Colors.BOLD}{'Type':<12} {'Amount':<12} {'Date':<24}{Colors.ENDC}")
        print("─" * 60)
        
        for transaction in transactions:
            if transaction['type'] == "Deposit":
                type_color = Colors.GREEN
            else:
                type_color = Colors.BLUE
            
            print(f"{type_color}{transaction['type']:<12}{Colors.ENDC} "
                  f"${transaction['amount']:<11.2f} {transaction['date']}")
        
        print("─" * 60)
    
    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")


if __name__ == "__main__":
    # Try to handle terminal that don't support ANSI colors
    try:
        os.system('color')  # Windows 10 support for ANSI
    except:
        # If colors aren't supported, make them empty strings
        for attr in dir(Colors):
            if not attr.startswith('__'):
                setattr(Colors, attr, '')
    
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print(f"\n{Colors.WARNING}Program terminated by user.{Colors.ENDC}")
        sys.exit(0)