from werkzeug.security import generate_password_hash
import csv
import faker
import random
import itertools

num_users = 1000
num_acct_hist = 1000
max_deposit_withdraw = 2000
num_acct_hist = 1000
max_deposit_withdraw = 2000
num_products = 907
num_inventory = 1000
max_in_stock = 50
num_carts = 1000
num_orders = 1000
max_order_contents = 10
num_reviews_prod = 1000
num_reviews_seller = 10

prod_images = ["https://cf.ltkcdn.net/small-pets/images/std/261832-800x533r1-brown-bunny.jpg", 
        "https://pbs.twimg.com/profile_images/447374371917922304/P4BzupWu.jpeg",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBhTbPjfcXMhJmid0xmld-_P-RwnYQnYwTYgRNV_zrG3AvbOmkXHlBKdlCipwrSJ_QFbA&usqp=CAU",
        "https://assets3.thrillist.com/v1/image/2962411/1200x600/scale;",
        "https://www.southernliving.com/thmb/90f6qLFHqn41zOIknnaJDiBebHw=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/GettyImages-10141026-1bunnies.-vikkihart-2000-7e25d19a2b5b4e8f8026cea5935826ed.jpg",
        "https://static9.depositphotos.com/1008280/1125/i/600/depositphotos_11250610-stock-photo-rabbit.jpg"]

faker.Faker.seed(0)
fake = faker.Faker()
random.seed(0)

def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

# generate user information with fake, ensuring that emails are not repeated
# returns lists of all uids and only the seller uids
def gen_users(num_users):
    lst_emails = []
    lst_emails = []
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        uids = []
        sell_uids = []
        for uid in range(num_users):
            uids.append(uid)
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            for i in range(100):
                profile = fake.profile()
                email = profile['mail']
                if email not in lst_emails:
                    break
            lst_emails.append(email)
            address = profile['address']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            is_seller = random.choice([0,1])
            if is_seller == 1:
                sell_uids.append(uid)
            writer.writerow([uid, firstname, lastname, address, email, password, is_seller])
        print(f'{num_users} generated')
    return uids, sell_uids

# generate account history for the users
def gen_account_history(num_acct_hist, uids, max_deposit_withdraw):
    with open('Account_History.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Account_History...', end=' ', flush=True)
        past_data = {}
        for entry in range(num_acct_hist):
            if entry % 10 == 0:
                print(f'{entry}', end=' ', flush=True)
            user_id = random.choice(uids)
            if user_id not in past_data.keys():
                past_data[user_id] = []
            # multiply potentially by -1 to withdraw money instead of deposit
            # make the multiplier for withdrawals small to hopefully avoid negative account balances
            sign = 1 if random.getrandbits(1) else -0.1
            amount = round(random.random() * max_deposit_withdraw * sign, 2)
            for i in range(100):
                time_stamp = fake.date_time()
                # ensures that a user does deposit/withdraw twice at the exact same time
                if time_stamp not in past_data[user_id]:
                    break
            past_data[user_id].append(time_stamp)
            writer.writerow([entry, user_id, amount, time_stamp])
        print(f'{num_acct_hist} generated')

# generate products for the database
def gen_products(num_products):
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)

        pids = []
        # load words from .txt files
        categories = open('categories.txt').read().splitlines()
        nouns = open('nouns.txt').read().splitlines()
        adjs = open('adjectives.txt').read().splitlines()
        random.shuffle(adjs)

        for pid in range(num_products):
            pids.append(pid)
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = adjs[pid] + " " + nouns[fake.random_int(max=len(nouns)-1)]
            category = categories[fake.random_int(max=len(categories)-1)]
            description = fake.paragraph(nb_sentences=3)
            image = prod_images[fake.random_int(max=len(prod_images) - 1)]
            price = float(f'{str(fake.random_int(max=100))}.{fake.random_int(max=99):02}')
            writer.writerow([pid, name, category, description, price, image])
        print(f'{num_products} generated')
    return pids

# generate inventory for sellers - use seller ids for the uids parameter to ensure that only sellers can sell
def gen_inventory(num_inventory, uids, pids, max_in_stock):
    with open('Inventory.csv', 'w') as f:
        inventory_pairs = []
        nonzero_inventory_pairs = []
        inventory_ids = []
        writer = get_csv_writer(f)
        print('Inventory...', end=' ', flush=True)
        # gets possible combinations of products and seller ids, and then samples randomly
        uid_pid_prod = list(itertools.product(uids, pids))
        rand_samples = random.sample(uid_pid_prod, num_inventory)
        # chooses whether the product is listed or not randomly
        is_active_values = random.choices([0,1], weights=[0.2, 0.8], k=num_inventory)
        for i in range(num_inventory):
            inventory_ids.append(i)
            if i % 100 == 0:
                print(f'{i}', end=' ', flush=True)
            uid = rand_samples[i][0]
            pid = rand_samples[i][1]
            is_active = is_active_values[i]
            choice = random.random()
            # chooses randomly how of this product does the seller have in stock
            if choice < 0.2:
                quantity = 0
            else:
                quantity = random.randint(0, max_in_stock)
            if is_active == 0:
                quantity = 0
            # maintains a separate list of inventory ids that have nonzero quantity
            if quantity > 0:
                nonzero_inventory_pairs.append([i, uid, pid, quantity])
            inventory_pairs.append([i, uid, pid, quantity, is_active])
            writer.writerow([i, uid, pid, quantity, is_active])
        print(f'{num_inventory} generated')
    return inventory_pairs, nonzero_inventory_pairs

# generate items in cart for users
def gen_cart(num_carts, max_order_contents, uids, nonzero_inventory_pairs):
    with open('Cart.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Cart...', end=' ', flush=True)
        # chooses inventories with nonzero quantities as candidates
        index_list = list(range(0,len(nonzero_inventory_pairs)))
        buyer_prod_combos = random.sample(set(itertools.product(uids, index_list)), num_carts)
        
        for i in range(num_carts):
            if i % 100 == 0:
                print(f'{i}', end=' ', flush=True)
            buy_uid = buyer_prod_combos[i][0]
            
            index = buyer_prod_combos[i][1]
            inv_select = nonzero_inventory_pairs[index]
            inventory_id = inv_select[0]
            sell_uid = inv_select[1]
            pid = inv_select[2]
            quant = random.randint(0, inv_select[3])
            status = "in_cart" if random.random() < 0.5 else "save_for_later"
            writer.writerow([i, buy_uid, sell_uid, inventory_id, pid, quant, status])

                
        print(f'{num_carts} generated')
        
# generate orders for the users
def gen_order(num_orders, uids):
    order_ids = []
    # keep a dictionary of user and time stamps they've submitted orders at
    past_data = {}
    with open('Specific_Order.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Order...', end=' ', flush=True)
        for i in range(num_orders):
            if i % 10 == 0:
                print(f'{i}', end=' ', flush=True)
            uid = random.choice(uids)
            if uid not in past_data.keys():
                past_data[uid] = []
            # ensures that time_stamp is unique for this user - tries up to 100 times to find a new time value if there are duplicates
            for j in range(100):
                time_stamp = fake.date_time()
                if time_stamp not in past_data[uid]:
                    break
            past_data[uid].append(time_stamp)
            order_ids.append([i, uid, time_stamp])
            writer.writerow([i, uid, time_stamp])
    return order_ids

# generate the contents of the previously generated orders
def gen_order_contents(max_order_contents, max_in_stock, order_ids, uids, inventory_pairs):
    with open('Order_Content.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Order Contents...', end=' ', flush=True)
        count = -1
        # iterates through the specific order ids
        for order in range(len(order_ids)):
            order_id = order_ids[order][0]
            if order % 10 == 0:
                print(f'{order}', end=' ', flush=True)
            # randomly chooses how many line items are in this order
            num_conts = random.randint(1, max_order_contents)
            # chooses a random sample of inventories from the inventory list - ensures that line items aren't duplicated
            inv_samples = random.sample(inventory_pairs, num_conts)
            for cont in range(num_conts):
                inv_select = inv_samples[cont]
                inv_id = inv_select[0]
                quant = random.randint(0, max_in_stock)
                price = float(f'{str(fake.random_int(max=30))}.{fake.random_int(max=99):02}')
                status = "fulfilled" if random.random() < 0.8 else "in_progress"
                count += 1
                writer.writerow([count, order_id, inv_id, quant, price, status])

# generates product reviews
def product_review(num_reviews_prod, pids, uids):
    with open('Product_Review.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Product_Review...', end=' ', flush=True)
        uid_pid_prod = list(itertools.product(uids, pids))
        rand_samples = random.sample(uid_pid_prod, num_reviews_prod)
        for id in range(num_reviews_prod):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = rand_samples[id][0]
            pid = rand_samples[id][1]
            time_reviewed = fake.date_time()
            rating = f'{str(fake.random_int(min=0,max=5))}'
            writer.writerow([id, uid, pid, time_reviewed, rating])
        print(f'{num_reviews_prod} generated')
    return


# generates seller reviews
def seller_review(num_reviews_seller, uids1, uids2):
    past = []
    with open('Seller_Review.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Seller_Review...', end=' ', flush=True)
        id = 0
        while id < num_reviews_seller:
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid1 = fake.random_element(elements=uids1)
            uid2 = fake.random_element(elements=uids2)
            time_reviewed = fake.date_time()
            rating = f'{str(fake.random_int(min=0,max=5))}'
            # ensure that users can't review themselves, and a user cannot review the same user twice
            if (uid1 != uid2) and tuple([uid1, uid2]) not in past:
                writer.writerow([id, uid1, uid2, time_reviewed, rating])
                past.append(tuple([uid1, uid2]))
                id += 1
        print(f'{num_reviews_seller} generated')
    return



uids, sell_uids = gen_users(num_users)
gen_account_history(num_acct_hist, uids, max_deposit_withdraw)
pids = gen_products(num_products)
inventory_pairs, nonzero_inventory_pairs = gen_inventory(num_inventory, sell_uids, pids, max_in_stock)
gen_cart(num_carts, max_order_contents, uids, nonzero_inventory_pairs)
order_ids = gen_order(num_orders, uids)
gen_order_contents(max_order_contents, max_in_stock, order_ids, uids, inventory_pairs)
product_review(num_reviews_prod, pids, uids)
seller_review(num_reviews_prod, uids, uids)
