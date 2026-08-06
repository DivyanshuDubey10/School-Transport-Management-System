import random
import security
from database import connect_database

def seed_database():
    conn = connect_database()
    cursor = conn.cursor()

    try:
        # Clear existing data (except admin)
        print("Clearing old data...")
        cursor.execute("TRUNCATE TABLE transport_change_request CASCADE;")
        cursor.execute("TRUNCATE TABLE student CASCADE;")
        cursor.execute("TRUNCATE TABLE parent CASCADE;")
        cursor.execute("TRUNCATE TABLE bus CASCADE;")
        cursor.execute("TRUNCATE TABLE route CASCADE;")
        
        # 1. Seed Routes
        print("Seeding routes...")
        routes_data = [
            "Vasant Kunj - Route A",
            "Dwarka Sector 10 - Route B",
            "Rohini - Route C",
            "Saket - Route D",
            "Gurugram Phase 1 - Route E"
        ]
        
        route_ids = []
        for r_name in routes_data:
            cursor.execute("INSERT INTO route (route_name) VALUES (%s) RETURNING route_id", (r_name,))
            route_ids.append(cursor.fetchone()[0])
            
        # 2. Seed Buses
        print("Seeding buses...")
        driver_names = ["Ramesh Kumar", "Suresh Singh", "Rajesh Sharma", "Vikram Patel", "Amit Verma"]
        bus_ids = []
        for i, r_id in enumerate(route_ids):
            bus_num = f"DL 1P {1000 + i}"
            capacity = random.choice([30, 40, 50])
            driver = driver_names[i]
            driver_phone = f"987654320{i}"
            cursor.execute(
                "INSERT INTO bus (bus_number, capacity, route_id, driver_name, driver_phone) VALUES (%s, %s, %s, %s, %s) RETURNING bus_id",
                (bus_num, capacity, r_id, driver, driver_phone)
            )
            bus_ids.append(cursor.fetchone()[0])
            
        # 3. Seed Parents
        print("Seeding parents...")
        parent_names = ["Arvind Kejriwal", "Sunita Sharma", "Priya Gupta", "Rahul Desai", "Anil Kapoor", "Meera Chopra", "Rajeev Singh", "Sonia Gandhi", "Kiran Rao", "Vikash Jain"]
        locations = ["Vasant Kunj Sector C", "Dwarka Mor", "Rohini Sector 11", "Saket J Block", "Gurugram DLF Phase 1", "Hauz Khas", "Green Park", "Lajpat Nagar", "Karol Bagh", "Pitampura"]
        
        parent_ids = []
        hashed_pw = security.hash_password("password123")
        for i in range(10):
            p_name = parent_names[i]
            phone = f"987654321{i}"
            address = f"{random.randint(1, 100)}, {locations[i]}, New Delhi"
            pickup = locations[i]
            username = f"parent{i+1}"
            
            cursor.execute(
                """
                INSERT INTO parent (parent_name, phone, address, pickup_point, username, password)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING parent_id
                """,
                (p_name, phone, address, pickup, username, hashed_pw)
            )
            parent_ids.append(cursor.fetchone()[0])
            
        # 4. Seed Students
        print("Seeding students...")
        first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Ayaan", "Krishna", "Ishaan", "Shaurya", "Saanvi", "Aanya", "Aadhya", "Aaradhya", "Ananya", "Pari", "Diya", "Navya", "Myra", "Ira"]
        classes = ["1A", "2B", "3C", "4A", "5B", "6C", "7A", "8B", "9C", "10A"]
        
        for i in range(25): # Create 25 students
            parent_id = random.choice(parent_ids)
            # Find the parent's last name
            cursor.execute("SELECT parent_name FROM parent WHERE parent_id = %s", (parent_id,))
            parent_last_name = cursor.fetchone()[0].split()[-1]
            
            s_name = f"{random.choice(first_names)} {parent_last_name}"
            s_class = random.choice(classes)
            r_id = random.choice(route_ids)
            fee_paid = random.choice([5000.0, 10000.0, 15000.0])
            fee_balance = random.choice([0.0, 2000.0, 5000.0])
            
            cursor.execute(
                """
                INSERT INTO student (student_name, student_class, parent_id, route_id, transport_status, fee_status, fee_paid, fee_balance)
                VALUES (%s, %s, %s, %s, 'Active', 'Active', %s, %s)
                """,
                (s_name, s_class, parent_id, r_id, fee_paid, fee_balance)
            )
            
        # Add a couple of change requests for the Review system demo
        print("Seeding pending requests...")
        for i in range(3):
            # pick random student
            cursor.execute("SELECT student_id, parent_id FROM student WHERE transport_status = 'Active' ORDER BY RANDOM() LIMIT 1")
            s_data = cursor.fetchone()
            if s_data:
                s_id = s_data[0]
                p_id = s_data[1]
                
                # pick a random new location
                new_pickup = random.choice(locations)
                
                cursor.execute(
                    "INSERT INTO transport_change_request (student_id, requested_pickup_point, status) VALUES (%s, %s, 'Pending')",
                    (s_id, new_pickup)
                )
            
        conn.commit()
        print("Database seeded successfully! Your dashboard is now Demo Ready.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_database()
