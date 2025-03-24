items = ['tomato', 'brinjal', 'potato', 'mirchi']
price = [20, 25, 40, 30]
quantity = [10.0, 20.0, 15.0, 20.0]
cost_price=[15,20,30,20]
sold_items = []  
sold_quantities = []  
customers=[]
customer_numbers=[]
Total_profit=[]
admin_username = "admin"
admin_password = "password123"


while True:
    print("1. Admin")
    print("2. Customer")
    print("3. Exit")
    print()
    who = (input("Enter your choice (1-3): "))
    print()
    if who == '1':
        username = input("Enter Username: ")
        print()
        password = input("Enter Password: ")
        print()
        if username == admin_username and password == admin_password:
            
            print('*'*10,"welcome to  Admin Portal",'*'*10)
            while True:
                print()
                print("1. Add Item")
                print("2. Remove Item")
                print("3. Modify Item")
                print("4. View Items")
                print("5. Customer Details")
                print("6. Itomized Profit")
                print("7. Profit")
                print("8. Exit")
                print()
                choice = (input("Enter your choice (1-8): "))

                # Adding a new item
                if choice == '1':
                    print()
                    name = input("Enter item name: ").lower()
                    if name in items:
                        print()
                        print(name, "already exists in the inventory!")
                    elif name.isdigit():
                        print()
                        print('Invalid Vegetable Name \nPlease Enter a valid Name')
                    else:
                        items.append(name)
                        idx = items.index(name)
                        prc = float(input("Enter selling price: "))
                        print()
                        qty = float(input("Enter item quantity: "))
                        print()
                        c_price=float(input("Enter cost_price: "))
                        price.insert(idx, prc)
                        quantity.insert(idx, qty)
                        cost_price.insert(idx, c_price)
                        print()
                        print("Item added successfully!")
                        #print("Items:", items)
                        #print("Prices:", price)
                        #print("Quantities:", quantity)
                        #print("cost_price",cost_price)

                # Removing an item
                elif choice == '2':
                    print()
                    name1 = input("Enter item name to remove: ").lower()
                    if name1 in items:
                        idx = items.index(name1)
                        items.pop(idx)
                        price.pop(idx)
                        quantity.pop(idx)
                        print()
                        print(name1, "removed successfully!")
                    else:
                        print()
                        print("Item not found!")
                    #print("Items:", items)
                    #print("Prices:", price)
                    #print("Quantities:", quantity)

                # Modifying an item
                elif choice == '3':
                    print()
                    name3 = input("Enter item name to modify: ").lower()
                    if name3 in items:
                        
                        idx = items.index(name3)
                        print()
                        new_price = float(input("Enter new selling price: "))
                        print()
                        new_quantity = int(input("Enter new quantity: "))
                        print()
                        new_cost_price = float(input("Enter cost price: "))
                        print()
                        price[idx] = new_price
                        quantity[idx] = new_quantity
                        cost_price[idx] = new_cost_price
                        print()
                        print(name3, "modified successfully!")
                    else:
                        print()
                        print("Item not found!")
                    #print("Items:", items)
                    #print("Prices:", price)
                    #print("Quantities:", quantity)

                # Viewing items
                elif choice =='4':
                    print()
                    print('' * 10, 'View Items', '' * 10)
                    print()
                    print("Item - Price - Quantity")
                    print()
                    for p, q, r in zip(items, price, quantity):
                        print(p, "-", q, "Rs/kg -", r, "kg")
                    print('*' * 32)


                elif choice=='5':
                    print()
                    print(f'Customer_Name{'':<5} Mobile_Number{'':<5}')
                    print()
                    if customers and customer_numbers:
                        for i,j in zip(customers,customer_numbers):
                            print()
                            print(f'{i:<20} {j:<10}')
                            print()
                    else:
                        print()
                        print('There is No Customers Still Now')
                        print()
                elif choice=='6':
                    
                    for item,quantity in zip(sold_items,sold_quantities):
                        idx=sold_items.index(item)
                        q=sold_quantities[idx]
                        oidx=items.index(item)
                        sp=price[oidx]
                        cp=cost_price[oidx]
                        profit=(sp-cp)*q
                        Total_profit.append(profit)
                        print()
                        print(f'Item_Name {'':<15} Profit{'':<5}')
                        print(f'{item:<20},{profit:<5}')
                        print()
                        #print(Total_profit)
                        

                elif choice=='7':
                    Final_profit=sum(Total_profit)
                    print()
                    print(f'Final_profit {Final_profit:>5}')
                    print()
                        
                elif choice == '8':
                    break

                else:
                    print()
                    print("Invalid input!")
                    print()
        else:
            print()
            print("Invalid Credentials")
            print()

                
    # Customer Section

    elif who == '2':  
        cart = []
        cart_quantity = []

        while True:
            print()
            print('*'*10,"Welcome to the Vegtable Inventory",'*'*10)
            print()
            print("1. Add to Cart")
            print("2. Remove from Cart")
            print("3. Modify Cart")
            print("4. View Cart")
            print("5. Billing")
            print("6. Exit")
            print()
            ch = input("Enter your choice (1-6): ")
            print()
            if ch == '1':
                
                for i, j, k in zip(items, price, quantity):
                    print(f'Item_Name {'':<10} Price {'':<10} Quantity {'':>5}')
                    print(i,'-', j, 'Rs/kg','-', k,' kg available')
                print()
                item = input("Enter item name to add: ").lower()
                print()
                qty = float(input("Enter quantity: "))
                print()
                if item in items:
                    idx = items.index(item)
                    if qty <= quantity[idx]:
                        if item in cart:
                            cart_idx = cart.index(item)
                            cart_quantity[cart_idx] += qty
                        else:
                            cart.append(item)
                            cart_quantity.append(qty)
                        quantity[idx] -= qty
                        print()
                        print("added successfully")
                        print()
                    else:
                        print()
                        print("Insufficient stock!")
                        print()
                else:
                    print()
                    print("Item not found!")
                    print()

            elif ch == '2':
                print()
                item = input("Enter item name to remove: ").lower()
                print()
                if item in cart:
                    idx = cart.index(item)
                    restored_qty = cart_quantity[idx]
                    item_idx = items.index(item)
                    quantity[item_idx] += restored_qty
                    cart.pop(idx)
                    cart_quantity.pop(idx)
                    print()
                    print("item removed")
                    print()
                else:
                    print()
                    print("Item not found in cart!")
                    print()

            elif ch == '3':
                print()
                item = input("Enter item name to modify in cart: ").lower()
                print()
                if item in cart:
                    idx = cart.index(item)
                    new_qty = float(input("Enter new quantity: "))
                    idx = cart.index(item)
                    cart_quantity[idx] = new_qty
                    print()
                    print("updated successfyully")
                    print()
                else:
                    print()
                    print("item not found in cart!")
                    print()

            elif ch == '4':
                print()
                print('' * 10, "The Items In Your Cart", '' * 10)
                print()
                if cart:
                    for j, k in zip(cart, cart_quantity):
                        print(f'Item {'':<10} Quantity {'':>5}')
                        print(j, "-", k, "kg")
                    print()
                else:
                    print()
                    print("There is no Items Cart is empty!")
                    print()
                print('*' * 31)

            elif ch == '5':
                print()
                customer_name = input("Enter your name: ")
                print()
                ph_no = input("Enter your mobile number: ")
                print()

                # Check if the phone number is already recorded
                if ph_no in customer_numbers:
                    print()
                    print("Your phone number is already in the customer records.")
                    print()
                else:
                    # phone number checking
                    if ph_no.isdigit() and len(ph_no) == 10:
                        # Check if the name already exists
                        if customer_name in customers:
                            print()
                            print("The name is already in the customer records, adding with new phone number.")
                            print()
                        else:
                            print()
                            print("Adding customer details")
                            print()
                        
                        # Append the new customer details
                        customers.append(customer_name)
                        customer_numbers.append(ph_no)
                        print()
                        print("Mobile number saved:", ph_no)
                        print()
                        # Proceed to billing details
                        if cart:
                            total_bill = 0
                            print()
                            print("Billing Details:")
                            print()
                            for item, qty in zip(cart, cart_quantity):
                                idx = items.index(item)
                                item_price = price[idx]
                                total = qty * item_price
                                print()
                                print(item, '-', qty, 'kg -', item_price, 'Rs/kg =', total, 'Rs')
                                print()
                                total_bill += total

                                # Append items and quantities to sold lists
                                if item in sold_items:
                                    sold_idx = sold_items.index(item)
                                    sold_quantities[sold_idx] += qty
                                else:
                                    sold_items.append(item)
                                    sold_quantities.append(qty)
                            print()
                            print("Total Amount to Pay:", total_bill, "Rs")
                            print()
                            cart.clear()
                            cart_quantity.clear()
                            print()
                            print("Thank you for shopping")
                            print()
                        else:
                            print()
                            print("Cart is empty")
                            print()
                    else:
                        print()
                        print("Invalid mobile number. Please enter a 10-digit number.")
                        print()
                        

                
                
                                        

            elif ch == '6':
                print()
                print("Exit")
                print()
                break

            else:
                print()
                print("Invalid input")
                print()
            
      
    elif who == '3':
        print()
        print("Exit")
        print()
        break

    else:
        print()
        print("Invalid input")
        print()
