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
        self.active_tickets = []
    
    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "active_tickets": self.active_tickets
        }

class Ticket:
    def __init__(self, title: str, description: str, priority: str, category: str, reporter: str):
        self.id = self._generate_ticket_id()
        self.title = title
        self.description = description
        self.priority = priority
        self.category = category
        self.reporter = reporter
        self.status = "new"
        self.assigned_to = ""
        self.created_date = datetime.datetime.now().isoformat()
        self.sla_deadline = self._calculate_sla_deadline()
        self.comments = []
    
    def _generate_ticket_id(self) -> str:
        """Generate unique ticket ID: TKT-YYYY-XXX"""
        year = datetime.datetime.now().year
        tickets = load_tickets()
        
        if not tickets:
            next_number = 1
        else:
            last_number = int(tickets[-1]["id"].split("-")[-1])
            next_number = last_number + 1
        
        return f"TKT-{year}-{next_number:03d}"
    
    def _calculate_sla_deadline(self) -> str:
        """Calculate SLA deadline based on priority"""
        priority_hours = {
            "urgent": 4,
            "high": 8,
            "medium": 24,
            "low": 48
        }
        
        hours = priority_hours.get(self.priority, 24)
        deadline = datetime.datetime.now() + datetime.timedelta(hours=hours)
        return deadline.isoformat()
    
    def to_dict(self) -> Dict:
        """Convert ticket object to dictionary for JSON storage"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "category": self.category,
            "reporter": self.reporter,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "created_date": self.created_date,
            "sla_deadline": self.sla_deadline,
            "comments": self.comments
        }

class Comment:
    def __init__(self, user: str, message: str):
        self.user = user
        self.message = message
        self.timestamp = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "user": self.user,
            "message": self.message,
            "timestamp": self.timestamp
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
        {"username": "admin", "password": "admin123", "role": "admin", "active_tickets": []},
        {"username": "tech", "password": "tech123", "role": "admin", "active_tickets": []},
        {"username": "user1", "password": "user123", "role": "user", "active_tickets": []},
        {"username": "user2", "password": "user123", "role": "user", "active_tickets": []}
    ]
    
    if not os.path.exists(USERS_FILE):
        save_users(default_users)
    else:
        existing_users = load_users()
        if not existing_users:
            save_users(default_users)

# ==================== AUTHENTICATION SYSTEM ====================
def authenticate_user() -> Optional[Dict]:
    """User authentication system"""
    print("\n🔐 LOGIN SYSTEM")
    print("=" * 30)
    
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()
    
    users = load_users()
    
    for user in users:
        if user["username"] == username and user["password"] == password:
            print(f"✅ Login successful! Welcome {username} ({user['role']})")
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
        "role": role,
        "active_tickets": []
    }
    users.append(new_user)
    save_users(users)
    
    print(f"✅ User {username} registered successfully as {role}!")

# ==================== CORE TICKET OPERATIONS ====================
def create_ticket(title: str, description: str, priority: str, category: str, reporter: str) -> str:
    """Create a new ticket"""
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority not in valid_priorities:
        return f"Error: Priority must be one of {valid_priorities}"
    
    new_ticket = Ticket(title, description, priority, category, reporter)
    ticket_dict = new_ticket.to_dict()
    
    tickets = load_tickets()
    tickets.append(ticket_dict)
    save_tickets(tickets)
    
    return f"Ticket created successfully! ID: {new_ticket.id}"

def get_ticket(ticket_id: str) -> Optional[Dict]:
    """Get ticket by ID"""
    tickets = load_tickets()
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    return None

def update_ticket_status(ticket_id: str, new_status: str, username: str = "system") -> str:
    """Update ticket status"""
    valid_statuses = ["new", "in_progress", "resolved", "closed"]
    if new_status not in valid_statuses:
        return f"Error: Status must be one of {valid_statuses}"
    
    tickets = load_tickets()
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            old_status = ticket["status"]
            ticket["status"] = new_status
            
            comment = Comment(
                username, 
                f"Status changed from {old_status} to {new_status}"
            )
            ticket["comments"].append(comment.to_dict())
            
            save_tickets(tickets)
            return f"Ticket {ticket_id} status updated to {new_status}"
    
    return f"Error: Ticket {ticket_id} not found"

def assign_ticket(ticket_id: str, technician: str) -> str:
    """Assign ticket to technician (admin only)"""
    if CURRENT_USER["role"] != "admin":
        return "Error: Only administrators can assign tickets!"
    
    tickets = load_tickets()
    users = load_users()
    
    technician_exists = any(user["username"] == technician for user in users)
    if not technician_exists:
        return f"Error: Technician {technician} not found"
    
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            old_assignee = ticket["assigned_to"]
            ticket["assigned_to"] = technician
            ticket["status"] = "in_progress"
            
            comment = Comment(
                "system",
                f"Ticket assigned from {old_assignee} to {technician} by {CURRENT_USER['username']}"
            )
            ticket["comments"].append(comment.to_dict())
            
            save_tickets(tickets)
            return f"Ticket {ticket_id} assigned to {technician}"
    
    return f"Error: Ticket {ticket_id} not found"

def add_comment(ticket_id: str, username: str, message: str) -> str:
    """Add comment to ticket"""
    tickets = load_tickets()
    
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            comment = Comment(username, message)
            ticket["comments"].append(comment.to_dict())
            
            if ticket["status"] == "new":
                ticket["status"] = "in_progress"
            
            save_tickets(tickets)
            return f"Comment added to ticket {ticket_id}"
    
    return f"Error: Ticket {ticket_id} not found"

# ==================== REPORTING & UTILITIES ====================
def check_sla_violations() -> List[Dict]:
    """Check for tickets nearing SLA breach"""
    tickets = load_tickets()
    violations = []
    
    current_time = datetime.datetime.now()
    
    for ticket in tickets:
        if ticket["status"] in ["closed", "resolved"]:
            continue
            
        sla_deadline = datetime.datetime.fromisoformat(ticket["sla_deadline"])
        time_remaining = sla_deadline - current_time
        hours_remaining = time_remaining.total_seconds() / 3600
        
        if hours_remaining < 0:
            # SLA already breached
            violations.append({
                "ticket": ticket["id"],
                "priority": ticket["priority"],
                "status": "breached",
                "hours_overdue": abs(hours_remaining)
            })
        elif hours_remaining < 2 and ticket["priority"] in ["urgent", "high"]:
            # Critical warning
            violations.append({
                "ticket": ticket["id"],
                "priority": ticket["priority"],
                "status": "critical_warning",
                "hours_remaining": hours_remaining
            })
        elif hours_remaining < 4 and ticket["priority"] in ["medium", "low"]:
            # Warning
            violations.append({
                "ticket": ticket["id"],
                "priority": ticket["priority"],
                "status": "warning",
                "hours_remaining": hours_remaining
            })
    
    return violations

def generate_reports() -> Dict:
    """Generate system reports"""
    tickets = load_tickets()
    
    if not tickets:
        return {"message": "No tickets available for reporting"}
    
    # Basic statistics
    total_tickets = len(tickets)
    open_tickets = len([t for t in tickets if t["status"] != "closed"])
    
    # Group by status
    status_count = {}
    for ticket in tickets:
        status = ticket["status"]
        status_count[status] = status_count.get(status, 0) + 1
    
    # Group by priority
    priority_count = {}
    for ticket in tickets:
        priority = ticket["priority"]
        priority_count[priority] = priority_count.get(priority, 0) + 1
    
    # SLA violations
    sla_violations = check_sla_violations()
    
    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "closed_tickets": status_count.get("closed", 0),
        "by_status": status_count,
        "by_priority": priority_count,
        "sla_violations": len(sla_violations),
        "sla_details": sla_violations
    }

def display_ticket(ticket: Dict) -> None:
    """Display ticket details in formatted way"""
    print(f"\n{'='*50}")
    print(f"TICKET: {ticket['id']}")
    print(f"{'='*50}")
    print(f"Title: {ticket['title']}")
    print(f"Description: {ticket['description']}")
    print(f"Status: {ticket['status']} | Priority: {ticket['priority']}")
    print(f"Category: {ticket['category']} | Reporter: {ticket['reporter']}")
    print(f"Assigned to: {ticket['assigned_to'] or 'Unassigned'}")
    print(f"Created: {ticket['created_date']}")
    print(f"SLA Deadline: {ticket['sla_deadline']}")
    
    if ticket['comments']:
        print(f"\nComments ({len(ticket['comments'])}):")
        for i, comment in enumerate(ticket['comments'], 1):
            print(f"  {i}. [{comment['timestamp']}] {comment['user']}: {comment['message']}")
    else:
        print("\nNo comments yet.")
    
    print(f"{'='*50}")

# ==================== MENU FLOWS ====================
def create_ticket_flow():
    """Flow for creating new ticket (available for all users)"""
    print("\n📝 CREATE NEW TICKET")
    title = input("Title: ").strip()
    description = input("Description: ").strip()
    priority = input("Priority (low/medium/high/urgent): ").strip().lower()
    category = input("Category: ").strip()
    
    # Auto-fill reporter based on current user
    reporter = CURRENT_USER["username"]
    
    if not all([title, description, priority, category]):
        print("❌ All fields are required!")
        return
        
    result = create_ticket(title, description, priority, category, reporter)
    print(f"✅ {result}")

def view_my_tickets_flow():
    """Flow for users to view only their tickets"""
    tickets = load_tickets()
    my_tickets = [t for t in tickets if t["reporter"] == CURRENT_USER["username"]]
    
    if not my_tickets:
        print("❌ You don't have any tickets yet.")
        return
        
    print(f"\n📋 MY TICKETS ({len(my_tickets)}):")
    for i, ticket in enumerate(my_tickets, 1):
        print(f"{i}. [{ticket['id']}] {ticket['title']} | Status: {ticket['status']} | Priority: {ticket['priority']}")
    
    view_details = input("\nView ticket details? (y/n): ").strip().lower()
    if view_details == 'y':
        ticket_id = input("Enter ticket ID: ").strip()
        ticket = get_ticket(ticket_id)
        if ticket and ticket["reporter"] == CURRENT_USER["username"]:
            display_ticket(ticket)
        else:
            print("❌ Ticket not found or access denied!")

def view_tickets_flow():
    """Flow for admin to view all tickets"""
    tickets = load_tickets()
    if not tickets:
        print("❌ No tickets found.")
        return
        
    print(f"\n📋 ALL TICKETS ({len(tickets)}):")
    for i, ticket in enumerate(tickets, 1):
        print(f"{i}. [{ticket['id']}] {ticket['title']} | Status: {ticket['status']} | Priority: {ticket['priority']}")
    
    view_details = input("\nView ticket details? (y/n): ").strip().lower()
    if view_details == 'y':
        ticket_id = input("Enter ticket ID: ").strip()
        ticket = get_ticket(ticket_id)
        if ticket:
            display_ticket(ticket)
        else:
            print("❌ Ticket not found!")

def add_comment_to_my_ticket_flow():
    """Flow for users to add comments only to their tickets"""
    ticket_id = input("Ticket ID: ").strip()
    
    # Check if user owns this ticket
    ticket = get_ticket(ticket_id)
    if not ticket:
        print("❌ Ticket not found!")
        return
        
    if ticket["reporter"] != CURRENT_USER["username"]:
        print("❌ You can only comment on your own tickets!")
        return
        
    message = input("Comment: ").strip()
    result = add_comment(ticket_id, CURRENT_USER["username"], message)
    print(f"✅ {result}")

def update_my_ticket_status_flow():
    """Flow for users to update status of their tickets"""
    ticket_id = input("Ticket ID: ").strip()
    
    # Check if user owns this ticket
    ticket = get_ticket(ticket_id)
    if not ticket:
        print("❌ Ticket not found!")
        return
        
    if ticket["reporter"] != CURRENT_USER["username"]:
        print("❌ You can only update your own tickets!")
        return
        
    new_status = input("New status (new/in_progress/resolved/closed): ").strip().lower()
    result = update_ticket_status(ticket_id, new_status, CURRENT_USER["username"])
    print(f"✅ {result}")

def assign_ticket_flow():
    """Flow for admin to assign tickets"""
    ticket_id = input("Ticket ID: ").strip()
    technician = input("Technician username: ").strip()
    
    result = assign_ticket(ticket_id, technician)
    print(f"✅ {result}")

def update_ticket_status_flow():
    """Flow for admin to update any ticket status"""
    ticket_id = input("Ticket ID: ").strip()
    new_status = input("New status (new/in_progress/resolved/closed): ").strip().lower()
    username = input("Your username: ").strip()
    
    result = update_ticket_status(ticket_id, new_status, username)
    print(f"✅ {result}")

def add_comment_flow():
    """Flow for admin to add comments to any ticket"""
    ticket_id = input("Ticket ID: ").strip()
    username = input("Your username: ").strip()
    message = input("Comment: ").strip()
    
    result = add_comment(ticket_id, username, message)
    print(f"✅ {result}")

def generate_reports_flow():
    """Flow for generating reports"""
    print("\n📊 SYSTEM REPORTS")
    reports = generate_reports()
    
    print(f"Total Tickets: {reports['total_tickets']}")
    print(f"Open Tickets: {reports['open_tickets']}")
    print(f"Closed Tickets: {reports['closed_tickets']}")
    print(f"\nBy Status: {reports['by_status']}")
    print(f"By Priority: {reports['by_priority']}")
    print(f"SLA Violations: {reports['sla_violations']}")
    
    if reports['sla_details']:
        print(f"\n🚨 SLA VIOLATION DETAILS:")
        for violation in reports['sla_details']:
            print(f"  - {violation['ticket']} ({violation['priority']}): {violation['status']}")

def check_sla_violations_flow():
    """Flow for checking SLA violations"""
    print("\n🚨 SLA VIOLATIONS CHECK")
    violations = check_sla_violations()
    
    if not violations:
        print("✅ No SLA violations detected!")
    else:
        print(f"❌ Found {len(violations)} SLA issues:")
        for violation in violations:
            print(f"  - {violation['ticket']} ({violation['priority']}): {violation['status']}")

def manage_users_flow():
    """Admin-only user management"""
    print("\n👤 USER MANAGEMENT")
    print("1. Register New User")
    print("2. List All Users")
    print("3. Back to Main Menu")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        register_user()
    elif choice == "2":
        users = load_users()
        print(f"\n📋 REGISTERED USERS ({len(users)}):")
        for user in users:
            role_icon = "👑" if user["role"] == "admin" else "👤"
            print(f"{role_icon} {user['username']} ({user['role']}) - Active tickets: {len(user['active_tickets'])}")
    elif choice == "3":
        return
    else:
        print("❌ Invalid choice!")

# ==================== ROLE-BASED MENU SYSTEM ====================
def show_admin_menu():
    """Display menu for admin users"""
    while True:
        print(f"\n👑 ADMIN MENU - Welcome {CURRENT_USER['username']}!")
        print("=" * 40)
        print("1. 📝 Create New Ticket")
        print("2. 👀 View All Tickets")
        print("3. 🔄 Update Ticket Status")
        print("4. 👥 Assign Ticket")
        print("5. 💬 Add Comment")
        print("6. 📊 Generate Reports")
        print("7. 🚨 Check SLA Violations")
        print("8. 👤 Manage Users")
        print("9. 🔐 Logout")
        print("0. ❌ Exit System")
        
        choice = input("\nEnter your choice (0-9): ").strip()
        
        if choice == "1":
            create_ticket_flow()
        elif choice == "2":
            view_tickets_flow()
        elif choice == "3":
            update_ticket_status_flow()
        elif choice == "4":
            assign_ticket_flow()
        elif choice == "5":
            add_comment_flow()
        elif choice == "6":
            generate_reports_flow()
        elif choice == "7":
            check_sla_violations_flow()
        elif choice == "8":
            manage_users_flow()
        elif choice == "9":
            print("🔐 Logging out...")
            break
        elif choice == "0":
            print("👋 Thank you for using Helpdesk System!")
            exit()
        else:
            print("❌ Invalid choice! Please try again.")

def show_user_menu():
    """Display menu for regular users"""
    while True:
        print(f"\n👤 USER MENU - Welcome {CURRENT_USER['username']}!")
        print("=" * 40)
        print("1. 📝 Create New Ticket")
        print("2. 👀 View My Tickets")
        print("3. 💬 Add Comment to My Ticket")
        print("4. 🔄 Update My Ticket Status")
        print("5. 🔐 Logout")
        print("0. ❌ Exit System")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "1":
            create_ticket_flow()
        elif choice == "2":
            view_my_tickets_flow()
        elif choice == "3":
            add_comment_to_my_ticket_flow()
        elif choice == "4":
            update_my_ticket_status_flow()
        elif choice == "5":
            print("🔐 Logging out...")
            break
        elif choice == "0":
            print("👋 Thank you for using Helpdesk System!")
            exit()
        else:
            print("❌ Invalid choice! Please try again.")

# ==================== MAIN APPLICATION ====================
def main():
    """Main application loop with authentication"""
    global CURRENT_USER
    
    print("🚀 HELP DESK TICKET SYSTEM")
    print("IPB University - D4 TPL")
    print("With Role-Based Access Control")
    
    # Initialize default users
    initialize_users()
    
    while True:
        print("\n" + "="*50)
        print("🔐 AUTHENTICATION REQUIRED")
        print("="*50)
        print("1. Login")
        print("2. Exit")
        
        auth_choice = input("\nEnter choice (1-2): ").strip()
        
        if auth_choice == "1":
            CURRENT_USER = authenticate_user()
            
            if CURRENT_USER:
                if CURRENT_USER["role"] == "admin":
                    show_admin_menu()
                else:
                    show_user_menu()
                    
        elif auth_choice == "2":
            print("👋 Thank you for using Helpdesk System!")
            break
        else:
            print("❌ Invalid choice! Please try again.")

if __name__ == "__main__":
    main()