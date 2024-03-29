
from h2o_wave import main, app, Q, ui

import os
import base64
import json

import requests
import cv2

import numpy as np

import torch
from torchvision.io import read_image
from torchvision.utils import draw_bounding_boxes
from torchvision.transforms.functional import to_pil_image


#URL = 'https://model.internal.dedicated.h2o.ai/9c67271f-4b10-4633-b417-a1b8413d5cb9/model/score'   # APIエンドポイント

# current directory(App実行 directory)上の元画像と結果画像のフォルダ
IMG_IN = 'images_in'        # インプット画像の格納フォルダ。App実行上のパスに配置
IMG_OUT = 'images_out'   # スコアリング実施後の画像の格納フォルダ。App実行上のパスに配置


def od_scoring(q: Q):
    '''
    スコアリングAPIに対しリクエストを実施し、結果（r）を取得
    '''
    img = cv2.imread(q.client.image_local_path)
    img_encode = base64.b64encode(cv2.imencode(".png", img)[1]).decode()
    data = {"fields": ["input"], "rows": [[img_encode]]}
    #r = requests.post(url=URL, json=data)   # スコアリングのリクエスト
    print('スコアリング直前のq.client.endpointurl: ', q.client.endpointurl)
    r = requests.post(url=q.client.endpointurl, json=data)   # スコアリングのリクエスト
    q.client.request_return = r

    image_processing(q)


def image_processing(q: Q):
    '''
    スコアリング結果の処理（閾値によるボックスの描画）と、処理画像の保存
    '''
    r = q.client.request_return
    ret = r.json()
    ret_json = json.loads(ret["score"][0][0])
    conf = np.array(ret_json['confidences'][0] )[np.array(ret_json['confidences'][0] ) >= q.client.threshold]   # threshold以上のConfidence
    b_boxes = np.array(ret_json['boxes'][0])[np.array(ret_json['confidences'][0] ) >= q.client.threshold]   # threshold以上のボックス
    q.client.n_box = len(conf)  # ボックスの数

    img_t = read_image(q.client.image_local_path)     # torch.Tensorとして画像を読み込む

    img_with_box = draw_bounding_boxes(   # 画像とボックスの重ね合わせ
        image=img_t,
        boxes=torch.from_numpy(b_boxes), 
        #labels=[str(i) for i in conf],   # Confidenceをラベルとする場合
        colors="red",
    )
    img_with_box = to_pil_image(img_with_box)    # PIL imageへ変換

    q.client.image_out_local_path = os.path.join(IMG_OUT, q.client.file_name)   # 結果画像の保存Local相対パス
    img_with_box.save(q.client.image_out_local_path)  # Localへ画像を保存


async def result_render(q: Q):
    '''
    スコアリング結果のレンダリング
    '''
    server_path = await q.site.upload([q.client.image_out_local_path])    # Wave Serverへ結果画像をアップ

    q.page['result_file'] = ui.markdown_card(
        box='6 2 3 5', 
        title='処理後の画像', 
        content='![original]({}) \n ボックスの数: {}'.format(server_path[0], q.client.n_box)   # 処理を実施した画像の表示
    )
    q.page['operation'] = ui.form_card(
        box='6 7 3 2',
        items=[
            ui.slider(name='slider', label='Confidence Level', min=0.1, max=1, step=0.05, value=q.client.threshold, trigger=True),
            ui.link(label="処理画像のダウンロード", download=True, path=server_path[0], button=False),
        ]
    )

async def endpoint_render(q: Q):
    '''
    エンドポイントURLのレンダリング
    '''
    print('q.args.endpointurl: ', q.args.endpointurl)
    print('q.client.endpointurl: ', q.client.endpointurl)
    q.page['endpoint'] = ui.form_card(
        box='1 2 2 1',
        items=[
            ui.textbox(name='endpointurl', label='APIエンドポイント', value=q.client.endpointurl, required=True),
        ]
    )

@app('/app')
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
        q.client.current_page = 'scoring'

        if q.client.endpointurl is None:   # APIエンドポイントがまだ入力されてない場合。入力してスコアリングが実施されると実行されない
            await endpoint_render(q)

        q.page['upload'] = ui.form_card(
            box='1 3 2 7',
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
            
            if q.client.endpointurl is None:   # APIエンドポイントの初期化。以降、そのエンドポイントを利用。新しいエンドポイントを設定する場合はブラウザリフレッシュか「このアプリに関して」へ
                q.client.endpointurl = q.args.endpointurl
            await endpoint_render(q)

            q.client.threshold = 0.5    # デフォルトでConfidence LevelのThresholdを0.5とする
            q.args.slider = q.client.threshold  # アップされるとSliderも初期化

            q.page['uploaded_file'] = ui.markdown_card(
                box='3 2 3 5', title='アップされた画像', 
                content='![original]({})'.format(q.args.file_upload[0])   # アップされた画像の表示
            )

            local_path = await q.site.download(q.args.file_upload[0], path=IMG_IN)   # local(app側)へDL
            q.client.image_local_path = local_path
            q.client.file_name = os.path.basename(q.client.image_local_path)   # インプットファイル名を取得（パスを除く）
            od_scoring(q)   # スコアリングの実施
            await result_render(q)

    else:  # ヘッダーの「このアプリに関して」をクリックした場合、もしくはデフォルト
        del q.page['upload'], q.page['uploaded_file'], q.page['result_file'], q.page['operation']
        q.client.current_page = 'readme'
        q.client.endpointurl = None
        
        q.page['readme'] = ui.tall_info_card(
            box='1 2 5 8', 
            name='',
            title='このアプリに関して', 
            caption='''
            このアプリは、投入した画像に対して画像の物体検出を実施します。\n
            「スコアリングの実施」実施画面に移動し、画像をドラッグ＆ドロップでアップして下さい。\n
            結果のバウンディングボックスの数は、Confidence Levelスライドバーで調整することができます。\n
            \n
            Source of photo： https://www.aetina.com/jp/solution.php?t=10
            ''',
            image='https://aismiley.co.jp/wp-content/uploads/2022/09/b-bpx_04-1320x643.jpg',
            image_height='300px')

    if q.args.slider:    # Confidence Levelスライダーが変更された場合の処理　
        if q.client.current_page == 'readme':    # 「このアプリに関して」の場合、処理を行わないようにする
            pass
        else:
            q.client.threshold = q.args.slider
            image_processing(q)
            await result_render(q)
    
    q.page['footer'] = ui.footer_card(box='1 10 8 1', caption='🚗... 🚙... 🚕...')

    print('q.args --->>> ', q.args)   # デバッグ用
    print('q.client --->>> ', q.client)   # デバッグ用
    await q.page.save()
