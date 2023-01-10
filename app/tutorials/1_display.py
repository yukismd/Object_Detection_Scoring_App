
from h2o_wave import main, app, Q, ui

@app('/demo1')
async def serve(q: Q):

    q.page['header'] = ui.header_card(
        box='1 1 8 1',
        title='自動車の物体検出',
        subtitle='投入した画像に映る自動車をバウンディングボックスで検出',
        icon='ParkingLocationMirrored',
    )
    q.page['content'] = ui.tall_info_card(
        box='1 2 5 8', 
        name='',
        title='このアプリに関して', 
        caption='''
        このアプリは、投入した画像に対して画像の物体検出を実施します。\n
        画像をドラッグ＆ドロップでアップして下さい。\n
        結果はConfidenceスライドバーで調整することができます。
        ''',
        image='https://aismiley.co.jp/wp-content/uploads/2022/09/b-bpx_04-1320x643.jpg',
        image_height='300px')

    q.page['footer'] = ui.footer_card(box='1 10 8 1', caption='🚗... 🚙... 🚕...')

    print('q.args --->>> ', q.args)   # デバッグ用
    await q.page.save()
