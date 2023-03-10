
from h2o_wave import main, app, Q, ui


@app('/demo0')
async def serve(q: Q):
    q.page['hello1'] = ui.markdown_card(box='1 1 3 3', title='Hello World!', content='こんにちは。')
    q.page['hello2'] = ui.markdown_card(box='4 1 3 3', title='Hello H2O Wave!', content='H2O Waveです。')

    await q.page.save()
