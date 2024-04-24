from database import create_database_and_tables, add_box, get_all_boxes, get_box, get_container, add_box_to_container, seed_data, get_all_container, get_all_freight, get_config
from tabulate import tabulate


def retrieve_numeric_input(called):
    input_ok = False
    n = None
    
    while not input_ok:
        n = input(f"\nEnter {called} ")
        
        try:
            
            n = float(n)
            input_ok = True
        except ValueError:
            print("Please provide a numeric input")
            
    return n

def add_box_menu():
    box_name = input("\nPlease enter name for the box: ")
    
    box_height = retrieve_numeric_input(called="the boxes height in meters")
    box_width = retrieve_numeric_input(called="the boxes width in meters")
    box_length = retrieve_numeric_input(called="the boxes length in meters")
    
    # add_box_to_database
    add_box(connection, (box_name, box_height, box_width, box_length))
    
def display_box_type():
    # call ab helper that returns all the box types in the db
    boxes = get_all_boxes(connection)
    
    
    print("\n" + tabulate(boxes,
        headers=["box_id", "box_name", "height", "width", "Length"],
        tablefmt="psql") + "\n"
        )

def load_box_menu():
    # asking for the box name
    n = input("Enter the name of the box: ")
    
    # validate wheter that exists
    box = get_box(connection, by_name=n)
    
    if not box:
        print("\nA box by that name could not be found. \n")
    else:
        box_dims = box.height * box.width * box.length
        container_id = input("Enter the id of the container to load the box: ")
    
    
    container = get_container(connection, container_id)
    
    if container is None or (container.occupied_volume + box_dims <= float(config.get('MAX_CONTAINER_STORAGE'))):
        
        add_box_to_container(connection, box.id, container_id)
    else: 
        print(f"Container {container_id} does not have enough space for box {box.id}")
    
def display_containers():
    containers = get_all_container(connection)
    print("\n" + tabulate(containers, headers=["container_id", "occupied_volume"],
                          tablefmt="fancy_grid") + "\n")   
    
def display_summary():
    freight = get_all_freight(connection)
    containers = get_all_container(connection) or ()
    
    nr_containers = len(containers)
    
    if not nr_containers:
        print("There is no contracted freight currently \n")
        return 
    
    contracted_voulme = sum([c.occupied_volume for c in containers])
    revenue = round(contracted_voulme * float(config.get('CUBIC_METER_CHARGEOUT')), 2)
    cost = nr_containers * float(config.get('COST_PER_CONTAINER'))
    
    print(f"Contracted {len(freight)} box(es) in {len(containers)}  containers(s).")
    print(f"The total contracted volume is {contracted_voulme} m3.")
    print(f"Estimated cost of carry this freight is: ${cost}")
    print(f"Estimated P/L: ${round(revenue - cost, 2)} \n")

def main_menu():
    print("Welcome to Freight Manager!\n")

    n = "no_op"

    while n.upper() != 'X':
        print("1. Add a box type\n2. Show box types\n3. Load box to container"
              "\n4. Show container\n5. Summary Report\nX. Close\n")

        n = input("Your choice: ")

        if n == "1":
            add_box_menu()
        elif n == "2":
            display_box_type()
        elif n == "3":
            load_box_menu()
        elif n == "4":
            display_containers()
        elif n == "5":
            display_summary()

    print("\nGoodbye!")


if __name__ == "__main__":
    connection = create_database_and_tables(filename="freight_prob.db")
    seed_data(connection)
    config = get_config(connection)
    main_menu()
    