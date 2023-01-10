
from h2o_wave import main, app, Q, ui

def image_processing(img):
    '''
    img: Localに配置してある画像のパス(not Wave Server path)
    画像への処理を実施し、処理後の画像のLocalパスを返す
    '''
    return img

@app('/demo3')
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
            box='1 2 2 8',
            items=[
                ui.text_m("画像（jpg, png）をアップして下さい。"),
                ui.file_upload(name='file_upload', 
                            label='Upload!', 
                            multiple=False,
                            file_extensions=['jpg', 'png'],   # 許可するファイル形式
                            max_file_size=5, 
                            max_size=5,
                )    # Uploadボタンを押すとWaveサーバにデータがアップされる（q.args.file_uploadがファイルパス）
            ]
        )

        if q.args.file_upload:   # 画像ファイルがアップされた場合の処理
            q.page['uploaded_file'] = ui.markdown_card(
                box='3 2 3 5', title='アップされた画像', 
                #content=str(q.args.file_upload),
                content='![original]({})'.format(q.args.file_upload[0])   # アップされた画像の表示
            )

            local_path = await q.site.download(q.args.file_upload[0], path='app_images')   # local(app側)へDL
            local_path_processed = image_processing(local_path)   # 画像処理を実施
            server_path = await q.site.upload([local_path_processed])    # Wave Serverへアップ

            q.page['result_file'] = ui.markdown_card(
                box='6 2 3 5', 
                title='処理後の画像', 
                content='![original]({})'.format(server_path[0])   # 処理を実施した画像の表示
            )
            q.page['operation'] = ui.form_card(
                box='6 7 3 1',
                items=[
                    ui.link(label="処理画像のダウンロード", download=True, path=server_path[0], button=False),
                ]
            )

    else:  # ヘッダーの「このアプリに関して」をクリックした場合、もしくはデフォルト
        del q.page['upload'], q.page['uploaded_file'], q.page['result_file'], q.page['operation']
        
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
