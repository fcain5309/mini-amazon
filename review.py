from datetime import datetime
from flask import render_template, redirect, url_for, request
from flask_login import current_user
from .models.product import Product
from .models.review import Product_Review
from .models.review import Seller_Review
from .models.user import User
from flask import Blueprint
bp = Blueprint('review', __name__)

#Search all reviews for users.
@bp.route("/reviewquery", methods = ["POST", "GET"])
def querypage():
    
#    print("--------------------------------")
#    for i in range(0,999,1):
#        print("this is i:",i)
#        if((Product_Review.get_all_purchases_by_uid(i) is None) == False):
#            for dev in Product_Review.get_all_purchases_by_uid(i):
#                print("This is the pid:",dev)


        
    if current_user.is_authenticated:
        return redirect(url_for("review.reviewresults",persid = current_user.id))
    else:
        purchases = None
    # render the page by adding information to the index.html file
        if request.method == "POST":
            idnum = request.form["nm"]
            
            return redirect(url_for("review.reviewresults",persid = idnum))
        else:
            return render_template("reviews.html")

@bp.route("/reviewquerypostlog", methods = ["POST", "GET"])
def querypagepostlogin():
 
    
    print("--------------------------------")
    for i in range(0,100,1):
        print("this is i:",i)
        if((Product_Review.get_all_purchases_by_uid(i) is None) == False):
            for dev in Product_Review.get_all_purchases_by_uid(i):
                print("This is the pid:",dev)


        

        purchases = None
    # render the page by adding information to the index.html file
    if request.method == "POST":
        idnum = request.form["nm"]
        
        return redirect(url_for("review.reviewresults",persid = idnum))
    else:
        return render_template("reviews.html")


@bp.route("/make_seller_review", methods = ["POST", "GET"])
def makesellerreview():
    revbev = ["0","1","2","3","4","5"]
    if request.method == "POST":
        idnum = request.form["iduser"]
        idsell = request.form["idsell"]
        review = request.form["review"]


        roi = Product_Review.get_all_purchases_by_uid(idnum)
        for x in roi:
            print(x)


        if(Product_Review.has_purchased_from_seller(int(idnum),int(idsell)) is None):
            print("You didn't buy from this seller so how can you make a review?")
            return render_template("reviews_seller_generate.html",failed = 1, revbev = revbev)


        else:
            print("You've bought a product from this seller so a review makes sense.")
            Seller_Review.register_seller_review(int(idnum),int(idsell),datetime.now().isoformat(sep=" ", timespec="seconds"),int(review))
            return redirect(url_for("review.reviewresults",persid = idnum))

        

    else:
        return render_template("reviews_seller_generate.html",failed = 0, revbev = revbev)

        
#original method for creating product reviews, with text boxes.
@bp.route("/make_product_review", methods = ["POST", "GET"])
def makeproductreview():
    revbev = ["0","1","2","3","4","5"]
    if request.method == "POST":
        idnum = request.form["iduser"]
        idprod = request.form["idsell"]
        review = request.form["review"]
#        neorev = request.form["neo_rev"]
#        print("This is neorev: ",neorev)
        roi = Product_Review.get_all_purchases_by_uid(idnum)
        for x in roi:
            print(x)


        if(Product_Review.has_purchased_product(int(idnum),int(idprod)) is None):
            print("You didn't buy this product, how can you make a review?")
            return render_template("reviews_product_generate.html",failed = 1, revbev = revbev)
        elif(Product_Review.has_already_reviewed(int(idnum), int(idprod)) is None):
            print("You've bought this product so a review makes sense.")
            now = datetime.now()
            Product_Review.register_product_review(int(idnum),int(idprod),datetime.now().isoformat(sep=" ", timespec="seconds"),int(review))
            return redirect(url_for("review.reviewresults",persid = idnum))
        else:
            print("You have already reviewed this product.")
            return render_template("reviews_product_generate.html",failed = 2, revbev = revbev)

        

    else:

        return render_template("reviews_product_generate.html",failed = 0, revbev = revbev)





#----------------------------------------------------
#Improved method for making seller review with dropdown menu.
@bp.route("/neo_make_seller_review/<persid>", methods = ["POST", "GET"])
def neomakesellerreview(persid):
    diction = {}
    sellids = []
    allboughtitems = Product_Review.get_all_purchases_by_uid(persid)
    if ((allboughtitems is None) == False):
        for item in allboughtitems:
            user_data = User.get_all_uid_data(item.seller_uid)
            sellids.append(user_data[0][1] + " " + user_data[0][2])
            diction.update({ user_data[0][1] + " " + user_data[0][2]: item.seller_uid})

#    sellids = [*set(sellids)]


    revbev = ["0","1","2","3","4","5"]
    if request.method == "POST":
        idnum = persid
        checkie = request.form["idsell"]
        idsell = diction[checkie]
        review = request.form["review"]



        roi = Product_Review.get_all_purchases_by_uid(idnum)
        for x in roi:
            print(x)


        if(Product_Review.has_purchased_from_seller(int(idnum),int(idsell)) is None):
            print("You didn't buy from this seller so how can you make a review?")
            return render_template("neo_reviews_seller_generate.html",failed = 1, revbev = revbev,sellids = sellids)


        elif(Seller_Review.has_already_reviewed(int(idnum), int(idsell)) is None):
            print("You've bought a product from this seller so a review makes sense.")
            Seller_Review.register_seller_review(int(idnum),int(idsell),datetime.now().isoformat(sep=" ", timespec="seconds"),int(review))
            return redirect(url_for("review.reviewresults",persid = idnum))
        else:
            print("You already have a reveiw for this seller so how can you make a review?")
            return render_template("neo_reviews_seller_generate.html",failed = 2, revbev = revbev,sellids = sellids)            

        

    else:
        return render_template("neo_reviews_seller_generate.html",failed = 0, revbev = revbev,sellids = sellids)

        
#Improved Product review fucntion with drop down.
@bp.route("/neo_make_product_review/<persid>", methods = ["POST", "GET"])
def neomakeproductreview(persid):
    diction = {}
    itemnames = []
    allboughtitems = Product_Review.get_all_purchases_by_uid(persid)
    if ((allboughtitems is None) == False):
        for item in allboughtitems:
            itemnames.append(item.name)
            diction.update({ item.name: item.pid})

    revbev = ["0","1","2","3","4","5"]
    if request.method == "POST":
        checkie = request.form["idsell"]
        idnum = persid
        idprod = diction[checkie]
        review = request.form["review"]
#        neorev = request.form["neo_rev"]
#        print("This is neorev: ",neorev)
        roi = Product_Review.get_all_purchases_by_uid(idnum)
        for x in roi:
            print(x)
        
        print("already reviewed ",Product_Review.has_already_reviewed(int(idnum), int(idprod)))
        if(Product_Review.has_purchased_product(int(idnum),int(idprod)) is None):
            print("You didn't buy this product, how can you make a review?")
            return render_template("reviews_product_generate.html",failed = 1, revbev = revbev)
        elif(Product_Review.has_already_reviewed(int(idnum), int(idprod)) is None):
            print("You've bought this product so a review makes sense.")
            now = datetime.now()
            Product_Review.register_product_review(int(idnum),int(idprod),datetime.now().isoformat(sep=" ", timespec="seconds"),int(review))
            return redirect(url_for("review.reviewresults",persid = idnum))
        else:
            print("You have already reviewed this product.")
            return render_template("neo_reviews_product_generate.html",failed = 2, revbev = revbev,sellids = itemnames)

        

    else:

        return render_template("neo_reviews_product_generate.html",failed = 0, revbev = revbev,sellids = itemnames)



#-----------------------------------------------------


#Method for making products with personalid and product id already established
@bp.route("/neo_make_product_review/<persid>/<neoid>", methods = ["POST", "GET"])
def neomakeproductreviewpreset(persid,neoid):
    diction = {}
    itemnames = []
    antidiction = {}
    reviewable = False
    revbev = ["0","1","2","3","4","5"]
    if(((Product_Review.has_purchased_product(int(persid),int(neoid)) is None) == False) and ((Product_Review.has_already_reviewed(int(persid),int(neoid)) is None) == True)):
        reviewable = True
        allboughtitems = Product_Review.get_all_purchases_by_uid(persid)



        if ((allboughtitems is None) == False):
            for item in allboughtitems:
                itemnames.append(item.name)
                diction.update({ item.name: item.pid})
                antidiction.update({ ""+str(item.pid): item.name})
        print("This is the Neoid:",neoid)
        stora = neoid
        print("Neo id:",neoid)
        print("antidiction: ",antidiction)
        print("antidiction",antidiction[""+str(neoid)])
        neoid = str(neoid)+","+str(antidiction[neoid])

        if request.method == "POST":
            checkie = stora
            idnum = persid
            idprod = stora
            review = request.form["review"]
    #        neorev = request.form["neo_rev"]
    #        print("This is neorev: ",neorev)
            roi = Product_Review.get_all_purchases_by_uid(idnum)
            for x in roi:
                print(x)


            if(Product_Review.has_purchased_product(int(idnum),int(idprod)) is None):
                print("You didn't buy this product, how can you make a review?")
                return render_template("neo_reviews_product_generate_preset.html",failed = 1, revbev = revbev,sellids = itemnames,neoid=neoid,reviewable = reviewable)
            elif(Product_Review.has_already_reviewed(int(idnum), int(idprod)) is None):
                print("You've bought this product so a review makes sense.")
                now = datetime.now()
                Product_Review.register_product_review(int(idnum),int(idprod),datetime.now().isoformat(sep=" ", timespec="seconds"),int(review))
                return redirect(url_for("review.reviewresults",persid = idnum))
            else:
                print("You have already reviewed this product.")
                return render_template("reviews_product_generate.html",failed = 2, revbev = revbev)


        else:

            return render_template("neo_reviews_product_generate_preset.html",failed = 0, revbev = revbev, sellids =itemnames,neoid=neoid,reviewable=reviewable)

    elif((Product_Review.has_purchased_product(int(persid),int(neoid)) is None) == True):
        print("Oops you can't review that")
        return render_template("neo_reviews_product_generate_preset.html",failed = 0, revbev = revbev, sellids=itemnames,neoid=neoid,reviewable=reviewable)
    else:
        print("Oops you can't review that becasuse you already have a reveiew")
        return render_template("neo_reviews_product_generate_preset.html",failed = 2, revbev = revbev, sellids=itemnames,neoid=neoid,reviewable=reviewable)


#-----------------------------------------------------


#------------------------------------------------

#Making seller review with sellerid and personal id already established
@bp.route("/neo_make_seller_reviewpreset/<persid>/<neoid>", methods = ["POST", "GET"])
def neomakesellerreviewpreset(persid,neoid):
    diction = {}
    itemnames = []
    antidiction = {}
    reviewable = False
    revbev = ["0","1","2","3","4","5"]
    sellids = []
    allboughtitems = Product_Review.get_all_purchases_by_uid(persid)
    if ((allboughtitems is None) == False):
        for item in allboughtitems:
            sellids.append(item.seller_uid)

    sellids = [*set(sellids)]
    if((Product_Review.has_purchased_from_seller(int(persid),int(neoid)) is None) == False and ((Seller_Review.has_already_reviewed(int(persid),int(neoid)) is None) == True)):
        reviewable = True
        allboughtitems = Product_Review.get_all_purchases_by_uid(persid)



#        if ((allboughtitems is None) == False):
#            for item in allboughtitems:
#                itemnames.append(item.name)
#                diction.update({ item.name: item.pid})
#                antidiction.update({ ""+str(item.pid): item.name})
  #      print("This is the Neoid:",neoid)
 #       stora = neoid
 #       print("Neo id:",neoid)
 #       print("antidiction: ",antidiction)
 #       print("antidiction",antidiction[""+str(neoid)])
 #       neoid = str(neoid)+","+str(antidiction[neoid])

        if request.method == "POST":
            checkie = neoid
            idnum = persid
            idprod = neoid
            review = request.form["review"]
    #        neorev = request.form["neo_rev"]
    #        print("This is neorev: ",neorev)
            roi = Product_Review.get_all_purchases_by_uid(idnum)
            for x in roi:
                print(x)


            if(Product_Review.has_purchased_from_seller(int(idnum),int(idprod)) is None):
                print("You didn't buy this product, how can you make a review?")
                return render_template("neo_reviews_seller_generate_preset.html",failed = 1, revbev = revbev,sellids = itemnames,neoid=neoid,reviewable = reviewable)


            else:
                print("You've bought this product so a review makes sense.")
                now = datetime.now()
                Product_Review.register_seller_review(int(idnum),int(idprod),datetime.now().isoformat(sep=" ", timespec="seconds"),int(review))
                return redirect(url_for("review.reviewresults",persid = idnum))

            

        else:

            return render_template("neo_reviews_seller_generate_preset.html",failed = 0, revbev = revbev, sellids =sellids,neoid=neoid,reviewable=reviewable)

    elif((Product_Review.has_purchased_from_seller(int(persid),int(neoid)) is None) == True):
        print("Oops you can't review that")
        return render_template("neo_reviews_seller_generate_preset.html",failed = 0, revbev = revbev, sellids=sellids,neoid=neoid,reviewable=reviewable)
    else:
        print("Oops you can't review that because you already have the reveiew")
        return render_template("neo_reviews_seller_generate_preset.html",failed = 2, revbev = revbev, sellids=sellids,neoid=neoid,reviewable=reviewable)


#-----------------------------------------------------

#Delete seller review method
@bp.route("/delete_seller_review/<persid>", methods = ["POST", "GET"])
def deletesellerreview(persid):
    persid = int(persid)
    persid = int(persid)
    diction = {}
    antidiction = {}
    sellids = []
    allboughtitems = Product_Review.get_all_purchases_by_uid(persid)
    if ((allboughtitems is None) == False):
        for item in allboughtitems:
            user_data = User.get_all_uid_data(item.seller_uid)
            sellids.append(user_data[0][1] + " " + user_data[0][2])
            diction.update({ user_data[0][1] + " " + user_data[0][2]: item.seller_uid})
            antidiction.update({ item.seller_uid : user_data[0][1] + " " + user_data[0][2]})
    if request.method == "POST":



        checkie = request.form["idsell"]
        idnum = persid
        idprod = diction[checkie]




        question =  Seller_Review.delete_seller_review(int(persid),int(idprod))

        print("This is question: ", question)
        if( question == 0):
            print("I'm in here")
            prodrev = Product_Review.get_all_by_uid(persid)
            if(len(prodrev) > 0):
                prodev = prodrev[:5]
            else:
                prodev = []
            userrev = Seller_Review.get_all_by_uid(persid)
            if(len(userrev) > 0):
                userrev = userrev[:5]
            else:
                userrev = []
        #   print("this is the persid: ",persid)
        #   print("Prod dev uid:",prodrev[0].uid)
            idarray = []
            for dev in userrev:
                print("This is one dev: ",dev.uid2)
                idarray.append(antidiction[dev.uid2])

            return render_template("deletesellerreview.html",name = persid, avail_reviews = prodev, avail_reviews_people = userrev,failure = 1,idarray=idarray,user = User)


        else:
            return redirect(url_for("review.reviewresults",persid = persid))
        

    else:
        prodrev = Product_Review.get_all_by_uid(persid)
        if(len(prodrev) > 0):
            prodev = prodrev[:5]
        else:
            prodev = []
        userrev = Seller_Review.get_all_by_uid(persid)
        if(len(userrev) > 0):
            userrev = userrev[:5]
        else:
            userrev = []
    #   print("this is the persid: ",persid)
    #   print("Prod dev uid:",prodrev[0].uid)
        idarray = []
        for dev in userrev:
            print("This is one dev: ",dev.uid2)
            idarray.append(antidiction[dev.uid2])
            
        return render_template("deletesellerreview.html",name = persid, avail_reviews = prodev, avail_reviews_people = userrev,failure = 0,idarray = idarray,user=User)
#        return render_template("deletesellerreview.html")

#Edit seller review method
@bp.route("/edit_seller_review/<persid>", methods = ["POST", "GET"])
def editsellerreview(persid):
    revbev = ["0","1","2","3","4","5"]
    persid = int(persid)
    antidiction = {}
    diction = {}
    sellids = []
    allboughtitems = Product_Review.get_all_purchases_by_uid(persid)
    if ((allboughtitems is None) == False):
        for item in allboughtitems:
            user_data = User.get_all_uid_data(item.seller_uid)
            sellids.append(user_data[0][1] + " " + user_data[0][2])
            diction.update({ user_data[0][1] + " " + user_data[0][2]: item.seller_uid})
            antidiction.update({ item.seller_uid : user_data[0][1] + " " + user_data[0][2]})
    if request.method == "POST":
        
        neoreview = request.form["neoreview"]
        checkie = request.form["idsell"]
        idnum = persid
        idprod = diction[checkie]

#        neorev = request.form["neo_rev"]
#        print("This is neorev: ",neorev)





        question =  Seller_Review.edit_seller_review(int(persid),int(idprod),datetime.now().isoformat(sep=" ", timespec="seconds"),neoreview)

        print("This is question: ", question)
        if( question == 0):
            print("I'm in here")
            prodrev = Product_Review.get_all_by_uid(persid)
            if(len(prodrev) > 0):
                prodev = prodrev[:5]
            else:
                prodev = []
            userrev = Seller_Review.get_all_by_uid(persid)
            if(len(userrev) > 0):
                userrev = userrev[:5]
            else:
                userrev = []
        #   print("this is the persid: ",persid)
        #   print("Prod dev uid:",prodrev[0].uid)
            idarray = []
            for dev in userrev:
                print("This is one dev: ",dev.uid2)
                idarray.append(dev.uid2)
            return render_template("editsellerreview.html",name = persid, avail_reviews = prodev, avail_reviews_people = userrev,failure = 1,revbev = revbev,idarray = idarray,user= User)


        else:
            return redirect(url_for("review.reviewresults",persid = persid))
        

        

    else:
        prodrev = Product_Review.get_all_by_uid(persid)
        if(len(prodrev) > 0):
            prodev = prodrev[:5]
        else:
            prodev = []
        userrev = Seller_Review.get_all_by_uid(persid)
        if(len(userrev) > 0):
            userrev = userrev[:5]
        else:
            userrev = []
    #   print("this is the persid: ",persid)
    #   print("Prod dev uid:",prodrev[0].uid)
        idarray = []
        for dev in userrev:
            print("This is one dev: ",dev.uid2)
            idarray.append(antidiction[dev.uid2])
        return render_template("editsellerreview.html",name = persid, avail_reviews = prodev, avail_reviews_people = userrev,failure = 0, revbev = revbev,idarray = idarray,user= User)
#        return render_template("deletesellerreview.html")


#Delete Product Review Method
@bp.route("/delete_product_review/<persid>", methods = ["POST", "GET"])
def deleteproductreview(persid):
    prodrev = Product_Review.get_all_by_uid(persid)

    neodiction = {}
    itemnames = []
    allboughtitems = Product_Review.get_all_purchases_by_uid(persid)

    if ((allboughtitems is None) == False):
        for item in allboughtitems:
            itemnames.append(item.name)
            neodiction.update({ item.name: item.pid})
    
    persid = int(persid)
    prodrev = Product_Review.get_all_by_uid(persid)
    diction = {}

    for dev in prodrev:
        print("This dev pid:",dev.pid)
        print("this is the personal id",persid)
        diction.update({dev.pid : Product.get(dev.pid).name})
    print ("This is diction: ",diction)
    if request.method == "POST":
        checkie = request.form["idsell"]
        idprod = neodiction[checkie]

        




        question =  Product_Review.delete_product_review(int(persid),int(idprod))

        print("This is question: ", question)
        if( question == 0):
            print("I'm in here")
            prodrev = Product_Review.get_all_by_uid(persid)
            if(len(prodrev) > 0):
                prodev = prodrev[:5]
            else:
                prodev = []
            userrev = Seller_Review.get_all_by_uid(persid)
            if(len(userrev) > 0):
                userrev = userrev[:5]
            else:
                userrev = []
        #   print("this is the persid: ",persid)
        #   print("Prod dev uid:",prodrev[0].uid)
            idarray = []
            for dev in prodev:
                print("This is one dev: ",dev.pid)
                idarray.append(diction[dev.pid])
            return render_template("deleteproductreview.html",name = persid, avail_reviews = prodev, avail_reviews_people = userrev,failure = 1,idarray=idarray,diction=diction)


        else:
            return redirect(url_for("review.reviewresults",persid = persid))
        

    else:
        prodrev = Product_Review.get_all_by_uid(persid)
        if(len(prodrev) > 0):
            prodev = prodrev[:5]
        else:
            prodev = []
        userrev = Seller_Review.get_all_by_uid(persid)
        if(len(userrev) > 0):
            userrev = userrev[:5]
        else:
            userrev = []
    #   print("this is the persid: ",persid)
    #   print("Prod dev uid:",prodrev[0].uid)
        idarray = []
        for dev in prodev:
            print("This is one dev: ",dev.pid)
            idarray.append(diction[dev.pid])
        return render_template("deleteproductreview.html",name = persid, avail_reviews = prodev, avail_reviews_people = userrev,failure = 0,idarray = idarray,diction=diction)
#        return render_template("deletesellerreview.html")


#Edit Product Review Method
@bp.route("/edit_product_review/<persid>", methods = ["POST", "GET"])
def editproductreview(persid):
    prodrev = Product_Review.get_all_by_uid(persid)

    neodiction = {}
    itemnames = []
    allboughtitems = Product_Review.get_all_purchases_by_uid(persid)

    if ((allboughtitems is None) == False):
        for item in allboughtitems:
            itemnames.append(item.name)
            neodiction.update({ item.name: item.pid})

    names = []
    diction = {}

    for dev in prodrev:
        print("This dev pid:",dev.pid)
        print("this is the personal id",persid)
        diction.update({dev.pid : Product.get(dev.pid).name})
    print ("This is diction: ",diction)
    revbev = ["0","1","2","3","4","5"]
    persid = int(persid)
    prodrev = Product_Review.get_all_by_uid(persid)
    if request.method == "POST":


        idprod = request.form["idsell"]
        neoreview = request.form["neoreview"]


        checkie = request.form["idsell"]
        idprod = neodiction[checkie]


        question =  Product_Review.edit_product_review(int(persid),int(idprod),datetime.now().isoformat(sep=" ", timespec="seconds"),neoreview)

        print("This is question: ", question)
        if( question == 0):
            print("I'm in here")

            if(len(prodrev) > 0):
                prodev = prodrev[:5]
            else:
                prodev = []
            userrev = Seller_Review.get_all_by_uid(persid)
            if(len(userrev) > 0):
                userrev = userrev[:5]
            else:
                userrev = []
        #   print("this is the persid: ",persid)
        #   print("Prod dev uid:",prodrev[0].uid)

            idarray = []
            for dev in prodev:
                print("This is one dev: ",dev.pid)
                idarray.append(diction[dev.pid])
        
            return render_template("editproductreview.html",name = persid, avail_reviews = prodev, avail_reviews_people = userrev,failure = 1,revbev = revbev,names = names, diction = diction,  sellids = idarray,idarray=idarray)


        else:
            return redirect(url_for("review.reviewresults",persid = persid))
        

        

    else:

        if(len(prodrev) > 0):
            prodev = prodrev[:5]
        else:
            prodev = []
        userrev = Seller_Review.get_all_by_uid(persid)
        if(len(userrev) > 0):
            userrev = userrev[:5]
        else:
            userrev = []
    #   print("this is the persid: ",persid)
    #   print("Prod dev uid:",prodrev[0].uid)
        idarray = []
        for dev in prodev:
            print("This is one dev: ",dev.pid)
            idarray.append(diction[dev.pid])

        return render_template("editproductreview.html",name = persid, avail_reviews = prodev, avail_reviews_people = userrev,failure = 0,revbev = revbev, names = names, diction = diction, sellids = idarray)
#        return render_template("deletesellerreview.html")




#Review results, meaning all reviews a person has made
@bp.route('/reviewresults/<persid>')
def reviewresults(persid):

    confirm = False
    prodrev = Product_Review.get_all_by_uid(persid)

    names = []
    diction = {}

    bought = 1

    picodev =Product_Review.get_all_purchases_by_uid(persid)



    if (picodev is None):
        bought = 0

    for dev in prodrev:
        print("This dev pid:",dev.pid)
        print("this is the personal id",persid)
        print("Crisp:",Product_Review.get_name_by_pid_and_uid(persid,dev.pid))
        diction.update({dev.pid : Product.get(dev.pid).name})
    print ("This is diction: ", diction)
    if(len(prodrev) > 0):
        prodev = prodrev[:5]
    else:
        prodev = []
    userrev = Seller_Review.get_all_by_uid(persid)
    if(len(userrev) > 0):
        userrev = userrev[:5]
    else:
        userrev = []

    if(current_user.is_authenticated and int(current_user.id) == int(persid)):
        confirm = True
        
    print("confirm ",confirm)
    return render_template("revresultswithsearch.html",name = persid, avail_reviews = prodev, avail_reviews_people = userrev,names = names,diction = diction, bought = bought, confirm = confirm,user = User)

#Page specifically for seller reveiws
@bp.route('/sellerreviews/<persid>')
def sellerreviews(persid):
    confirm = False
    
    name = User.get_name(persid)
    userrev = Seller_Review.get_all_about_seller(persid)
    avgrev = Seller_Review.get_seller_avg(persid)
    if(len(userrev) > 0):
        userrev = userrev[:5]
    else:
        userrev = []

    if(current_user.is_authenticated and int(current_user.id) == int(persid)):
        confirm = True
        
    print("confirm ",confirm)
    return render_template("reviews_about_seller.html",name = name, uid = persid, avail_reviews_people = userrev, avgrev=avgrev, confirm = confirm,user = User)

