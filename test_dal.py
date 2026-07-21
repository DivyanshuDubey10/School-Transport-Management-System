import sqlite3
from dal import db_dal

def run_tests():
    print("--- Starting DAL Tests ---")
    
    # 1. Route Management
    print("\n[Route Management]")
    test_route_name = "TEST_ROUTE_XYZ"
    res = db_dal.add_route(test_route_name)
    print(f"add_route: {'PASS' if res else 'FAIL'}")
    
    routes = db_dal.get_all_routes(search_query="TEST_ROUTE")
    print(f"get_all_routes (search): {'PASS' if len(routes) > 0 else 'FAIL'} (found {len(routes)})")
    
    route_id = routes[-1][0] if routes else None
    if route_id:
        res = db_dal.update_route(route_id, test_route_name + "_UPDATED")
        print(f"update_route: {'PASS' if res else 'FAIL'}")
        routes = db_dal.get_all_routes(search_query="TEST_ROUTE_XYZ_UPDATED")
        print(f"Verify update_route: {'PASS' if len(routes) > 0 else 'FAIL'}")
    
    # 2. Bus Management
    print("\n[Bus Management]")
    test_bus_num = "TEST-BUS-99"
    if route_id:
        res = db_dal.add_bus(test_bus_num, "Test Driver", "555-0000", 50, route_id)
        print(f"add_bus: {'PASS' if res else 'FAIL'}")
        
        buses = db_dal.get_all_buses()
        test_bus = next((b for b in buses if b[1] == test_bus_num), None)
        print(f"get_all_buses: {'PASS' if test_bus else 'FAIL'}")
        
        bus_id = test_bus[0] if test_bus else None
    else:
        bus_id = None
        print("Skipping bus tests due to missing route")

    # 3. Parent Management
    print("\n[Parent Management]")
    test_parent_user = "test_parent_user"
    res = db_dal.add_parent("Test Parent", "555-1111", "Test Address", "Test Point", test_parent_user, "hashed_pw")
    print(f"add_parent: {'PASS' if res else 'FAIL'}")
    
    parents = db_dal.get_all_parents(search_query="Test Parent")
    print(f"get_all_parents (search): {'PASS' if len(parents) > 0 else 'FAIL'}")
    
    parent_id = parents[-1][0] if parents else None
    if parent_id:
        res = db_dal.update_parent(parent_id, "Test Parent Updated", "555-1112", "New Addr", "New Point", test_parent_user)
        print(f"update_parent: {'PASS' if res else 'FAIL'}")
    
    # 4. Student Management
    print("\n[Student Management]")
    if parent_id and route_id:
        res = db_dal.add_student("Test Student", "10A", parent_id, route_id, 1000.0, 500.0)
        print(f"add_student: {'PASS' if res else 'FAIL'}")
        
        students = db_dal.get_all_students(search_query="Test Student")
        print(f"get_all_students (search): {'PASS' if len(students) > 0 else 'FAIL'}")
        
        student_id = students[-1][0] if students else None
        if student_id:
            res = db_dal.update_student(student_id, "Test Student Updated", "10B", parent_id, route_id, 1500.0, 0.0)
            print(f"update_student: {'PASS' if res else 'FAIL'}")
    else:
        student_id = None
        print("Skipping student tests due to missing parent/route")

    # 5. Dashboard & Auth Functions
    print("\n[Dashboard & Misc Functions]")
    stats = db_dal.get_dashboard_stats()
    print(f"get_dashboard_stats: {'PASS' if 'total_students' in stats else 'FAIL'} (Data: {stats})")
    
    admin = db_dal.get_admin_by_username("admin")
    print(f"get_admin_by_username: {'PASS' if admin else 'FAIL (Admin not found)'}")
    
    parent_check = db_dal.get_parent_by_username(test_parent_user)
    print(f"get_parent_by_username: {'PASS' if parent_check else 'FAIL'}")
    
    if parent_id:
        parent_dashboard_students = db_dal.get_parent_dashboard_students(parent_id)
        print(f"get_parent_dashboard_students: {'PASS' if len(parent_dashboard_students) > 0 else 'FAIL'}")

    routes_bus_dd = db_dal.get_all_routes_with_bus_dropdown()
    print(f"get_all_routes_with_bus_dropdown: {'PASS' if len(routes_bus_dd) > 0 else 'FAIL'}")
    
    parents_dd = db_dal.get_all_parents_dropdown()
    print(f"get_all_parents_dropdown: {'PASS' if len(parents_dd) > 0 else 'FAIL'}")
    
    if route_id:
        cap_check = db_dal.check_bus_capacity(route_id)
        print(f"check_bus_capacity: {'PASS' if cap_check else 'FAIL'} {cap_check}")

    # 6. Cleanup Data
    print("\n[Cleanup]")
    if student_id:
        res = db_dal.delete_student(student_id)
        print(f"delete_student: {'PASS' if res else 'FAIL'}")
    
    if parent_id:
        res = db_dal.delete_parent(parent_id)
        print(f"delete_parent: {'PASS' if res else 'FAIL'}")
    
    if bus_id:
        res = db_dal.delete_bus(bus_id)
        print(f"delete_bus: {'PASS' if res else 'FAIL'}")
        
    if route_id:
        res = db_dal.delete_route(route_id)
        print(f"delete_route: {'PASS' if res else 'FAIL'}")

    print("\n--- Testing Complete ---")

if __name__ == "__main__":
    run_tests()
