
from h2o_wave import main, app, Q, ui

@app('/demo2')
async def serve(q: Q):

    q.page['header'] = ui.header_card(
        box='1 1 8 1',
        title='自動車の物体検出',
        subtitle='投入した画像に映る自動車をバウンディングボックスで検出',
        icon='ParkingLocationMirrored',
        items=[
            ui.button(name='#readme', label='このアプリに関して', link=True),
            ui.button(name='#scoring', label='スコアリングの実施', link=True),],
    )

    if q.args['#'] == 'scoring':  # ヘッダーの「スコアリングの実施」をクリックした場合
        del q.page['readme']

        q.page['upload'] = ui.form_card(
            box='1 2 3 8',
            items=[
                ui.text_l("画像（jpg, png）をアップして下さい。"),
                ui.file_upload(name='file_upload', 
                            label='Upload!', 
                            multiple=False,
                            file_extensions=['jpg', 'png'],   # 許可するファイル形式
                            max_file_size=5, 
                            max_size=5,
                )    # Uploadボタンを押すとWaveサーバにデータがアップされる（q.args.file_uploadがファイルパス）
            ]
        )
    else:  # ヘッダーの「このアプリに関して」をクリックした場合、もしくはデフォルト
        del q.page['upload']

        q.page['readme'] = ui.tall_info_card(
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
