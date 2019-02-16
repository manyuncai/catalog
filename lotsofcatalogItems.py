from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Base, CatalogItem, User

engine = create_engine('sqlite:///catalogdatabasewithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user

User1 = User(name="Manyu Cai", email="manyuncai@yahoo.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# catalog items for Scoccer
catagory1 = Catalog(user_id=1,category="Soccer")

session.add(catagory1)
session.commit()

catalogItem1 = CatalogItem(user_id=1,title="soccer cleats",
                     description="cleans dirt and soil from the field", catalog=catagory1)

session.add(catalogItem1)
session.commit()


catalogItem2 = CatalogItem(user_id=1,title="Two Shinguards",
                     description="protct shins", catalog=catagory1)

session.add(catalogItem2)
session.commit()

catalogItem3 = CatalogItem(user_id=1,title="Goalkeeper Groves",
                     description="adidas Predator Fingersave Junior Soccer Goalkeeper Gloves", catalog=catagory1)

session.add(catalogItem3)
session.commit()
# catalog items for Basketball
catagory2 = Catalog(user_id=1,category="Basketball")

session.add(catagory2)
session.commit()

catalogItem1 = CatalogItem(user_id=1,title="Ball",
                     description="Champaignship baskeball",catalog=catagory2)

session.add(catalogItem1)
session.commit()


catalogItem2 = CatalogItem(user_id=1,title="Outfits",
                     description="Boys outfit top and bottom",catalog=catagory2)


session.add(catalogItem2)
session.commit()

catagory3 = Catalog(user_id=1,category="Football")

session.add(catagory3)
session.commit()

catalogItem1 = CatalogItem(user_id=1,title="NFL FootBall",
                     description="Wilson NFL official football",catalog=catagory3)

session.add(catalogItem1)
session.commit()


catalogItem2 = CatalogItem(user_id=1,title="Practice Jersey",
                     description="Nike Youth core football practice jersey",catalog=catagory3)


session.add(catalogItem2)
session.commit()

catalogItem3 = CatalogItem(user_id=1,title="Receiver Gloves",
                     description="Nike Youth vapor jet receiver gloves",catalog=catagory3)


session.add(catalogItem3)
session.commit()

catalogItem4 = CatalogItem(user_id=1,title="Forearm Sleeve",
                     description="Adidas audult padded compression forearm sleeve",catalog=catagory3)


session.add(catalogItem4)
session.commit()

catagory4 = Catalog(user_id=1,category="Tennis")

session.add(catagory4)
session.commit()
catalogItem1 = CatalogItem(user_id=1,title="Tennis FootBall",
                     description="Penn Championship extra duty tennis balls - 12 cans",catalog=catagory4)

session.add(catalogItem1)
session.commit()


catalogItem2 = CatalogItem(user_id=1,title="Hat",
                     description="Nike women's featherlight aerobill tennis visor",catalog=catagory4)


session.add(catalogItem2)
session.commit()
catalogItem3 = CatalogItem(user_id=1,title="Racquet",
                     description="Bobolat drive max 110 tennis racquet",catalog=catagory4)

session.add(catalogItem3)
session.commit()

print "added menu items!"
