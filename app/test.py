from app.core.containers import Container
import asyncio
app = Container()

alembic = app.alchemy_api.provided()
settings_rep = app.repository_order.provided()
db = app.db.provided()

for order in settings_rep.list():
    db.session.delete(order)

db.session.commit()
# print(settings_rep.create({
#     "minimum_bitcoin": 0,
#     "minimum_usdt": 0,
#     "minimum_etherium": 0,
#     "percent_from_buy_crypto": 0,
# }))
# wh_pyc1kzrbljdmbd7y
# print(asyncio.run(alembic.create_webhook("ETH_GOERLI", "ADDRESS_ACTIVITY", "https://5247-85-249-53-75.eu.ngrok.io/api/v1/webhook/erc-20")))
# print(asyncio.run(settings_rep.add_addresses_to_web_hook("wh_67ephm5rsturilde",['0x96a956bfe9d12f2e1ed0fa1377ddb70fa77d7773'], [])))
# print(asyncio.run(settings_rep.convert_from_wei(1000000000000000000000000000000000)))
