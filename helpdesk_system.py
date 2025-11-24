import json
import datetime
import os
import getpass
from typing import Dict, List, Optional

# File constants
TICKETS_FILE = "tickets.json"
USERS_FILE = "users.json"
CURRENT_USER = None

class User:
    def __init__(self, username: str, password: str, role: str):
        self.username = username
        self.password = password
        self.role = role
    
    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role
        }

class Ticket:
    def __init__(self, title: str, description: str, priority: str, reporter: str):
        self.id = self._generate_ticket_id()
        self.title = title
        self.description = description
        self.priority = priority
        self.reporter = reporter
        self.status = "new"
        self.created_date = datetime.datetime.now().isoformat()
        self.comments = []
    
    def _generate_ticket_id(self) -> str:
        """Generate unique ticket ID: TKT-XXX"""
        tickets = load_tickets()
        next_number = len(tickets) + 1
        return f"TKT-{next_number:03d}"
    
    def to_dict(self) -> Dict:
        """Convert ticket object to dictionary for JSON storage"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "reporter": self.reporter,
            "status": self.status,
            "created_date": self.created_date,
            "comments": self.comments
        }

# ==================== DATA STORAGE FUNCTIONS ====================
def load_tickets() -> List[Dict]:
    """Load tickets from JSON file"""
    try:
        with open(TICKETS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tickets(tickets: List[Dict]) -> None:
    """Save tickets to JSON file"""
    with open(TICKETS_FILE, 'w') as f:
        json.dump(tickets, f, indent=2)

def load_users() -> List[Dict]:
    """Load users from JSON file"""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_users(users: List[Dict]) -> None:
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def initialize_users():
    """Initialize default users if not exists"""
    default_users = [
        {"username": "admin", "password": "admin123", "role": "admin"},
        {"username": "tech", "password": "tech123", "role": "admin"},
        {"username": "user1", "password": "user123", "role": "user"},
        {"username": "user2", "password": "user123", "role": "user"}
    ]
    
    if not os.path.exists(USERS_FILE):
        save_users(default_users)

# ==================== SEARCHING & SORTING FUNCTIONS ====================
def search_tickets(keyword: str) -> List[Dict]:
    """Fungsi searching akan memfilter tiket berdasarkan keyword"""
    tickets = load_tickets()
    results = []
    
    if not keyword.strip():
        return tickets
    
    for ticket in tickets:
        # Search in title, description, dan reporter
        if (keyword.lower() in ticket['title'].lower() or 
            keyword.lower() in ticket['description'].lower() or 
            keyword.lower() in ticket['reporter'].lower() or
            keyword.lower() in ticket['id'].lower()):
            results.append(ticket)
    
    return results

def sort_tickets(tickets: List[Dict], sort_by: str, ascending: bool = True) -> List[Dict]:
    """Fungsi sorting akan mengurutkan tiket berdasarkan field yang dipilih"""
    if not tickets:
        return tickets
        
    if sort_by == "date":
        key = lambda x: x['created_date']
    elif sort_by == "priority":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        key = lambda x: priority_order[x['priority']]
    elif sort_by == "status":
        status_order = {"new": 0, "in_progress": 1, "resolved": 2}
        key = lambda x: status_order[x['status']]
    elif sort_by == "title":
        key = lambda x: x['title'].lower()
    else:
        return tickets
    
    return sorted(tickets, key=key, reverse=not ascending)

# ==================== AUTHENTICATION SYSTEM ====================
def authenticate_user() -> Optional[Dict]:
    """User authentication system"""
    print("\n🔐 LOGIN")
    print("=" * 20)
    
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()
    
    users = load_users()
    
    for user in users:
        if user["username"] == username and user["password"] == password:
            print(f"✅ Welcome {username}!")
            return user
    
    print("❌ Invalid username or password!")
    return None

def register_user():
    """Register new user (admin only)"""
    if CURRENT_USER["role"] != "admin":
        print("❌ Only administrators can register new users!")
        return
    
    print("\n👤 REGISTER NEW USER")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()
    role = input("Role (admin/user): ").strip().lower()
    
    if role not in ["admin", "user"]:
        print("❌ Role must be 'admin' or 'user'!")
        return
    
    users = load_users()
    
    # Check if username exists
    if any(user["username"] == username for user in users):
        print("❌ Username already exists!")
        return
    
    # Add new user
    new_user = {
        "username": username,
        "password": password,
        "role": role
    }
    users.append(new_user)
    save_users(users)
    
    print(f"✅ User {username} registered successfully as {role}!")

def delete_user():
    """Delete user (admin only)"""
    if CURRENT_USER["role"] != "admin":
        print("❌ Only administrators can delete users!")
        return
    
    print("\n🗑️ DELETE USER")
    username = input("Username to delete: ").strip()
    
    if username == CURRENT_USER["username"]:
        print("❌ You cannot delete your own account!")
        return
    
    users = load_users()
    
    for user in users:
        if user["username"] == username:
            # Konfirmasi penghapusan
            confirm = input(f"Are you sure you want to delete user '{username}'? (y/n): ").strip().lower()
            if confirm == 'y':
                users.remove(user)
                save_users(users)
                print(f"✅ User {username} deleted successfully!")
            else:
                print("❌ User deletion cancelled.")
            return
    
    print("❌ User not found!")

# ==================== CORE TICKET OPERATIONS ====================
def create_ticket(title: str, description: str, priority: str, reporter: str) -> str:
    """Create a new ticket"""
    valid_priorities = ["low", "medium", "high"]
    if priority not in valid_priorities:
        return f"Error: Priority must be one of {valid_priorities}"
    
    new_ticket = Ticket(title, description, priority, reporter)
    ticket_dict = new_ticket.to_dict()
    
    tickets = load_tickets()
    tickets.append(ticket_dict)
    save_tickets(tickets)
    
    return f"Ticket created! ID: {new_ticket.id}"

def get_ticket(ticket_id: str) -> Optional[Dict]:
    """Get ticket by ID"""
    tickets = load_tickets()
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    return None

def update_ticket_status(ticket_id: str, new_status: str) -> str:
    """Update ticket status"""
    valid_statuses = ["new", "in_progress", "resolved"]
    if new_status not in valid_statuses:
        return f"Error: Status must be one of {valid_statuses}"
    
    tickets = load_tickets()
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["status"] = new_status
            save_tickets(tickets)
            return f"Ticket {ticket_id} status updated to {new_status}"
    
    return f"Error: Ticket {ticket_id} not found"

def add_comment(ticket_id: str, username: str, message: str) -> str:
    """Add comment to ticket"""
    tickets = load_tickets()
    
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            comment = {
                "user": username,
                "message": message,
                "timestamp": datetime.datetime.now().isoformat()
            }
            ticket["comments"].append(comment)
            
            if ticket["status"] == "new":
                ticket["status"] = "in_progress"
            
            save_tickets(tickets)
            return f"Comment added to ticket {ticket_id}"
    
    return f"Error: Ticket {ticket_id} not found"

def delete_ticket(ticket_id: str) -> str:
    """Delete ticket (admin can delete any, user can only delete their own)"""
    tickets = load_tickets()
    
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            # Check permissions
            if CURRENT_USER["role"] != "admin" and ticket["reporter"] != CURRENT_USER["username"]:
                return "❌ You can only delete your own tickets!"
            
            # Konfirmasi penghapusan
            confirm = input(f"Are you sure you want to delete ticket '{ticket_id}'? (y/n): ").strip().lower()
            if confirm != 'y':
                return "❌ Ticket deletion cancelled."
            
            tickets.remove(ticket)
            save_tickets(tickets)
            return f"✅ Ticket {ticket_id} deleted successfully!"
    
    return f"❌ Ticket {ticket_id} not found"

# ==================== DISPLAY FUNCTIONS ====================
def display_ticket(ticket: Dict) -> None:
    """Display ticket details in formatted way"""
    print(f"\n{'='*40}")
    print(f"TICKET: {ticket['id']}")
    print(f"{'='*40}")
    print(f"Title: {ticket['title']}")
    print(f"Description: {ticket['description']}")
    print(f"Status: {ticket['status']} | Priority: {ticket['priority']}")
    print(f"Reporter: {ticket['reporter']}")
    print(f"Created: {ticket['created_date'][:16]}")
    
    if ticket['comments']:
        print(f"\nComments ({len(ticket['comments'])}):")
        for i, comment in enumerate(ticket['comments'], 1):
            print(f"  {i}. {comment['user']}: {comment['message']}")
    else:
        print("\nNo comments yet.")
    
    print(f"{'='*40}")

def display_tickets_summary(tickets: List[Dict], title: str):
    """Display summary list of tickets"""
    if not tickets:
        print(f"❌ No {title} found.")
        return
        
    print(f"\n📋 {title.upper()} ({len(tickets)}):")
    for i, ticket in enumerate(tickets, 1):
        status_icon = "🟢" if ticket["status"] == "new" else "🟡" if ticket["status"] == "in_progress" else "🔵"
        print(f"{i}. {status_icon} [{ticket['id']}] {ticket['title']} | Priority: {ticket['priority']}")

# ==================== SEARCH & SORT FLOWS ====================
def search_tickets_flow():
    """Flow untuk mencari tiket"""
    print("\n🔍 SEARCH TICKETS")
    keyword = input("Enter search keyword: ").strip()
    
    results = search_tickets(keyword)
    
    if not results:
        print("❌ No tickets found matching your search.")
        return results
    
    print(f"\n✅ Found {len(results)} tickets matching '{keyword}':")
    display_tickets_summary(results, "search results")
    
    # Tanya user apakah ingin sorting hasil search
    sort_option = input("\nSort results? (y/n): ").strip().lower()
    if sort_option == 'y':
        results = sort_tickets_flow(results)
    
    return results

def sort_tickets_flow(tickets: List[Dict] = None) -> List[Dict]:
    """Flow untuk mengurutkan tiket"""
    if tickets is None:
        tickets = load_tickets()
    
    if not tickets:
        print("❌ No tickets to sort.")
        return tickets
    
    print("\n📊 SORT TICKETS")
    print("1. By Date (newest first)")
    print("2. By Date (oldest first)")
    print("3. By Priority (high to low)")
    print("4. By Priority (low to high)")
    print("5. By Status")
    print("6. By Title (A-Z)")
    
    choice = input("Choose sort option (1-6): ").strip()
    
    if choice == "1":
        sorted_tickets = sort_tickets(tickets, "date", ascending=False)
        print("✅ Sorted by date (newest first)")
    elif choice == "2":
        sorted_tickets = sort_tickets(tickets, "date", ascending=True)
        print("✅ Sorted by date (oldest first)")
    elif choice == "3":
        sorted_tickets = sort_tickets(tickets, "priority", ascending=False)
        print("✅ Sorted by priority (high to low)")
    elif choice == "4":
        sorted_tickets = sort_tickets(tickets, "priority", ascending=True)
        print("✅ Sorted by priority (low to high)")
    elif choice == "5":
        sorted_tickets = sort_tickets(tickets, "status", ascending=True)
        print("✅ Sorted by status")
    elif choice == "6":
        sorted_tickets = sort_tickets(tickets, "title", ascending=True)
        print("✅ Sorted by title (A-Z)")
    else:
        print("❌ Invalid choice. Returning unsorted tickets.")
        return tickets
    
    # Tampilkan hasil sorting
    display_tickets_summary(sorted_tickets, "sorted tickets")
    return sorted_tickets

# ==================== USER MANAGEMENT FLOW ====================
def manage_users_flow():
    """Admin-only user management"""
    print("\n👤 USER MANAGEMENT")
    print("1. Register New User")
    print("2. List All Users")
    print("3. Delete User")
    print("4. Back to Main Menu")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        register_user()
    elif choice == "2":
        users = load_users()
        print(f"\n📋 REGISTERED USERS ({len(users)}):")
        for user in users:
            role_icon = "👑" if user["role"] == "admin" else "👤"
            print(f"{role_icon} {user['username']} ({user['role']})")
    elif choice == "3":
        delete_user()
    elif choice == "4":
        return
    else:
        print("❌ Invalid choice!")

# ==================== DELETE TICKET FLOWS ====================
def delete_ticket_flow():
    """Flow untuk menghapus tiket"""
    print("\n🗑️ DELETE TICKET")
    ticket_id = input("Enter ticket ID to delete: ").strip()
    
    result = delete_ticket(ticket_id)
    print(f" {result}")

def delete_my_ticket_flow():
    """Flow untuk user menghapus tiket mereka sendiri"""
    print("\n🗑️ DELETE MY TICKET")
    
    # Tampilkan tiket user terlebih dahulu
    tickets = load_tickets()
    my_tickets = [t for t in tickets if t["reporter"] == CURRENT_USER["username"]]
    
    if not my_tickets:
        print("❌ You don't have any tickets to delete.")
        return
    
    display_tickets_summary(my_tickets, "my tickets")
    
    ticket_id = input("\nEnter ticket ID to delete: ").strip()
    
    # Verifikasi bahwa tiket memang milik user
    ticket = get_ticket(ticket_id)
    if not ticket:
        print("❌ Ticket not found!")
        return
        
    if ticket["reporter"] != CURRENT_USER["username"]:
        print("❌ You can only delete your own tickets!")
        return
    
    result = delete_ticket(ticket_id)
    print(f" {result}")

# ==================== MENU FLOWS ====================
def create_ticket_flow():
    """Flow for creating new ticket"""
    print("\n📝 CREATE NEW TICKET")
    title = input("Title: ").strip()
    description = input("Description: ").strip()
    priority = input("Priority (low/medium/high): ").strip().lower()
    
    if not all([title, description, priority]):
        print("❌ All fields are required!")
        return
        
    result = create_ticket(title, description, priority, CURRENT_USER["username"])
    print(f"✅ {result}")

def view_my_tickets_flow():
    """Flow for users to view only their tickets"""
    tickets = load_tickets()
    my_tickets = [t for t in tickets if t["reporter"] == CURRENT_USER["username"]]
    
    if not my_tickets:
        print("❌ You don't have any tickets yet.")
        return
    
    display_tickets_summary(my_tickets, "my tickets")
    
    # Tampilkan options untuk search dan sort
    print("\n1. View Ticket Details")
    print("2. Search in My Tickets")
    print("3. Sort My Tickets")
    print("4. Delete My Ticket")
    
    choice = input("Choose option (1-4): ").strip()
    
    if choice == "1":
        ticket_id = input("Enter ticket ID: ").strip()
        ticket = get_ticket(ticket_id)
        if ticket and ticket["reporter"] == CURRENT_USER["username"]:
            display_ticket(ticket)
        else:
            print("❌ Ticket not found or access denied!")
    elif choice == "2":
        search_tickets_flow()
    elif choice == "3":
        sort_tickets_flow(my_tickets)
    elif choice == "4":
        delete_my_ticket_flow()

def view_all_tickets_flow():
    """Flow for admin to view all tickets"""
    tickets = load_tickets()
    
    if not tickets:
        print("❌ No tickets found.")
        return
    
    display_tickets_summary(tickets, "all tickets")
    
    # Tampilkan options untuk admin
    print("\n1. View Ticket Details")
    print("2. Search Tickets")
    print("3. Sort Tickets")
    print("4. Delete Ticket")
    
    choice = input("Choose option (1-4): ").strip()
    
    if choice == "1":
        ticket_id = input("Enter ticket ID: ").strip()
        ticket = get_ticket(ticket_id)
        if ticket:
            display_ticket(ticket)
        else:
            print("❌ Ticket not found!")
    elif choice == "2":
        search_tickets_flow()
    elif choice == "3":
        sort_tickets_flow(tickets)
    elif choice == "4":
        delete_ticket_flow()

def add_comment_flow():
    """Flow for adding comments to tickets"""
    ticket_id = input("Ticket ID: ").strip()
    
    # For regular users, check if they own the ticket
    if CURRENT_USER["role"] == "user":
        ticket = get_ticket(ticket_id)
        if ticket and ticket["reporter"] != CURRENT_USER["username"]:
            print("❌ You can only comment on your own tickets!")
            return
    
    message = input("Comment: ").strip()
    result = add_comment(ticket_id, CURRENT_USER["username"], message)
    print(f"✅ {result}")

def update_ticket_status_flow():
    """Flow for updating ticket status"""
    ticket_id = input("Ticket ID: ").strip()
    
    # For regular users, check if they own the ticket
    if CURRENT_USER["role"] == "user":
        ticket = get_ticket(ticket_id)
        if ticket and ticket["reporter"] != CURRENT_USER["username"]:
            print("❌ You can only update your own tickets!")
            return
    
    new_status = input("New status (new/in_progress/resolved): ").strip().lower()
    result = update_ticket_status(ticket_id, new_status)
    print(f"✅ {result}")

def generate_reports_flow():
    """Simple reporting"""
    print("\n📊 SYSTEM REPORT")
    tickets = load_tickets()
    
    if not tickets:
        print("No tickets available.")
        return
    
    total_tickets = len(tickets)
    status_count = {}
    priority_count = {}
    
    for ticket in tickets:
        status = ticket["status"]
        priority = ticket["priority"]
        status_count[status] = status_count.get(status, 0) + 1
        priority_count[priority] = priority_count.get(priority, 0) + 1
    
    print(f"Total Tickets: {total_tickets}")
    print(f"By Status: {status_count}")
    print(f"By Priority: {priority_count}")

# ==================== ROLE-BASED MENU SYSTEM ====================
def show_admin_menu():
    """Display menu for admin users"""
    while True:
        print(f"\n👑 ADMIN MENU - Welcome {CURRENT_USER['username']}!")
        print("=" * 30)
        print("1. 📝 Create Ticket")
        print("2. 👀 View All Tickets")
        print("3. 🔄 Update Status")
        print("4. 💬 Add Comment")
        print("5. 🔍 Search Tickets")
        print("6. 📊 Sort Tickets")
        print("7. 🗑️ Delete Ticket")
        print("8. 📈 Reports")
        print("9. 👤 Manage Users")
        print("10. 🔐 Logout")
        
        choice = input("\nEnter choice (1-10): ").strip()
        
        if choice == "1":
            create_ticket_flow()
        elif choice == "2":
            view_all_tickets_flow()
        elif choice == "3":
            update_ticket_status_flow()
        elif choice == "4":
            add_comment_flow()
        elif choice == "5":
            search_tickets_flow()
        elif choice == "6":
            sort_tickets_flow()
        elif choice == "7":
            delete_ticket_flow()
        elif choice == "8":
            generate_reports_flow()
        elif choice == "9":
            manage_users_flow()
        elif choice == "10":
            print("🔐 Logging out...")
            break
        else:
            print("❌ Invalid choice!")

def show_user_menu():
    """Display menu for regular users"""
    while True:
        print(f"\n👤 USER MENU - Welcome {CURRENT_USER['username']}!")
        print("=" * 30)
        print("1. 📝 Create Ticket")
        print("2. 👀 View My Tickets")
        print("3. 🔄 Update My Ticket")
        print("4. 💬 Comment on My Ticket")
        print("5. 🔍 Search My Tickets")
        print("6. 📊 Sort My Tickets")
        print("7. 🗑️ Delete My Ticket")
        print("8. 🔐 Logout")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == "1":
            create_ticket_flow()
        elif choice == "2":
            view_my_tickets_flow()
        elif choice == "3":
            update_ticket_status_flow()
        elif choice == "4":
            add_comment_flow()
        elif choice == "5":
            search_tickets_flow()
        elif choice == "6":
            # Untuk user, hanya sort ticket mereka sendiri
            my_tickets = [t for t in load_tickets() if t["reporter"] == CURRENT_USER["username"]]
            sort_tickets_flow(my_tickets)
        elif choice == "7":
            delete_my_ticket_flow()
        elif choice == "8":
            print("🔐 Logging out...")
            break
        else:
            print("❌ Invalid choice!")

# ==================== MAIN APPLICATION ====================
def main():
    """Main application loop"""
    global CURRENT_USER
    
    print("🚀 SIMPLE HELP DESK SYSTEM")
    print("With Search, Sort, Delete & User Management")
    
    # Initialize default users
    initialize_users()
    
    while True:
        print("\n" + "="*30)
        print("1. Login")
        print("2. Exit")
        
        choice = input("\nEnter choice (1-2): ").strip()
        
        if choice == "1":
            CURRENT_USER = authenticate_user()
            
            if CURRENT_USER:
                if CURRENT_USER["role"] == "admin":
                    show_admin_menu()
                else:
                    show_user_menu()
                    
        elif choice == "2":
            print("👋 Thank you!")
            break
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()