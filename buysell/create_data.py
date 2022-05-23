from os import lseek
from market.models import db
db.drop_all()
db.create_all()


from market.models import User,Item,Request

u1 = User(username='seller1',password_hash='$2b$12$PtHJui729T/mqYP3FqZmH.BS1OGhmuSGNi3fDSroxQ92yISB92z72',email_address='riky.manish@outlook.com')
db.session.add(u1)


u2 = User(username='seller2',password_hash='$2b$12$PtHJui729T/mqYP3FqZmH.BS1OGhmuSGNi3fDSroxQ92yISB92z72',email_address='s2@s2.com')
db.session.add(u2)


u3 = User(username='buysell',password_hash='$2b$12$PtHJui729T/mqYP3FqZmH.BS1OGhmuSGNi3fDSroxQ92yISB92z72',email_address='bs@bs.com')
db.session.add(u3)


u4 = User(username='buyer1',password_hash='$2b$12$PtHJui729T/mqYP3FqZmH.BS1OGhmuSGNi3fDSroxQ92yISB92z72',email_address='b1@b1.com')
db.session.add(u4)

u5 = User(username='buyer2',password_hash='$2b$12$PtHJui729T/mqYP3FqZmH.BS1OGhmuSGNi3fDSroxQ92yISB92z72',email_address='b2@b2.com')
db.session.add(u5)



item1 = Item(name='name1',price=1000,pickup_address='1A',description='desc',owner=1)
db.session.add(item1)
item2 = Item(name='name2',price=1000,pickup_address='1A',description='desc',owner=1)
db.session.add(item2)
item3 = Item(name='name3',price=1000,pickup_address='2A',description='desc',owner=2)
db.session.add(item3)
item4 = Item(name='name4',price=1000,pickup_address='2A',description='desc',owner=2)
db.session.add(item4)
item5 = Item(name='name5',price=1000,pickup_address='3A',description='desc',owner=3)
db.session.add(item5)

'''
req1 = Request(item_id=1,buyer_id=2,seller_id=1,status=0)
db.session.add(req1)

req2 = Request(item_id=1,buyer_id=3,seller_id=1,status=0)
db.session.add(req2)

req3 = Request(item_id=3,buyer_id=3,seller_id=2,status=0)
db.session.add(req3)

req4 = Request(item_id=3,buyer_id=4,seller_id=2,status=0)
db.session.add(req4)

req4 = Request(item_id=3,buyer_id=5,seller_id=2,status=0)
db.session.add(req4)
'''

db.session.commit()


