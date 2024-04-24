from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import os
import locale

app = Flask(__name__)


@app.route('/index', methods=['GET'])
def cartazesAuto():
    # Configurar o locale para usar o formato de moeda brasileira
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    # Obter os dados da imagem, o diretório e os dados do item da requisição
    data = request.json
    image_base64 = data.get('imagem_base64', '')
    directory = data.get(
        'directory', '')
    item = data.get('item', {})

    try:
        # Decodificar a imagem base64 para bytes
        image_bytes = base64.b64decode(image_base64)

        # Criar um objeto Image a partir dos bytes decodificados
        image = Image.open(io.BytesIO(image_bytes))

        # Criar um objeto ImageDraw.Draw para desenhar na imagem
        draw = ImageDraw.Draw(image)

        # Definir as fontes e tamanhos de texto
        fontDescricao = ImageFont.truetype('font_principal.ttf', 185)
        fontPreco = ImageFont.truetype('font_preco.ttf', 185)
        fontCodprod = ImageFont.truetype('font_principal.ttf', 30)
        fontembalagem = ImageFont.truetype('font_principal.ttf', 50)
        fontInfo = ImageFont.truetype('font_principal.ttf', 55)
        fontmarca = ImageFont.truetype('font_principal.ttf', 70)
        fontpromo = ImageFont.truetype('font_secundaria.ttf', 50)

        # Obter as dimensões da imagem
        largura, altura = image.size

        # Definir as coordenadas para o texto
        # DESCRIÇÃO
        bboxDescricao = draw.textbbox((0, 0), str(item['descricao']), font=fontDescricao)
        largura_texto = bboxDescricao[2] - bboxDescricao[0]
        altura_texto = bboxDescricao[3] - bboxDescricao[1]
        x_centro = (largura - largura_texto) // 2
        y_centro = (altura - altura_texto) // 3
        descricaoXY = (x_centro, y_centro - 100)

        # INFO
        bboxinfo = draw.textbbox((0, 0), str(item['informacao']), font=fontInfo)
        largura_info = bboxinfo[2] - bboxinfo[0]
        altura_info = bboxinfo[3] - bboxinfo[1]
        x_centro_info = (largura - largura_info) // 2
        y_centro_info = (altura - altura_info) // 2
        infoXY = (x_centro_info, y_centro_info - 285)

        # MARCA
        bboxmarca = draw.textbbox((0, 0), str(item['marca']), font=fontmarca)
        largura_marca = bboxmarca[2] - bboxmarca[0]
        altura_marca = bboxmarca[3] - bboxmarca[1]
        x_centro_marca = (largura - largura_marca) // 2
        y_centro_marca = (altura - altura_marca) // 2
        marcaXY = (x_centro_marca, y_centro_marca - 230)

        # CODPROD
        bboxcodprod = draw.textbbox((0, 0), "COD "+str(item['codprod']), font=fontCodprod)
        largura_codprod = bboxcodprod[2] - bboxcodprod[0]
        altura_codprod = bboxcodprod[3] - bboxcodprod[1]
        x_centro_codprod = (largura - largura_codprod) // 2
        y_centro_codprod = (altura - altura_codprod) // 2
        codprodXY = (x_centro_codprod - 5, y_centro_codprod - 175)

        embalagemXY = (900, 1300)
        promoXY = (100, 975)
        apartiXY = (100, 1025)
        precoXY = (85, 1050)

        # Verificar se item é um dicionário e contém as chaves necessárias
        if not isinstance(item, dict):
            raise ValueError("Item deve ser um dicionário")

        keys = ['descricao', 'informacao', 'marca', 'codprod', 'oldprice', 'newprice', 'embalagem']
        for key in keys:
            if key not in item:
                raise ValueError(f"A chave '{key}' não foi encontrada em 'item'")
        
        # Converter os preços para moeda brasileira
        old_price_str = locale.currency(item['oldprice'], grouping=True, symbol=None).replace('R$', '').strip()
        new_price_str = locale.currency(item['newprice'], grouping=True, symbol=None).replace('R$', '').strip()


        # Converter os valores para string se necessário e desenhar o texto na imagem
        draw.text(descricaoXY, str(item['descricao']),fill='black', font=fontDescricao)
        draw.text(infoXY, str(item['informacao']),fill='black', font=fontInfo)
        draw.text(marcaXY, str(item['marca']),fill='black', font=fontmarca)
        draw.text(codprodXY, "COD "+str(item['codprod']),fill='black', font=fontCodprod)
        draw.text(embalagemXY, str(item['embalagem']),fill='black', font=fontembalagem)
        draw.text(promoXY, "DE: R$"+old_price_str,fill='black', font=fontpromo)
        draw.text(precoXY, "R$"+new_price_str,fill='red', font=fontPreco)
        draw.text(apartiXY, "APARTIR DE:",fill='black', font=fontembalagem)

        # Definir o caminho completo do arquivo
        img_filename = f"item_{item['codprod']}.png"
        img_path = os.path.join(directory, img_filename)

        # Verificar se o diretório existe e, se não, criá-lo
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Salvar a imagem no diretório especificado
        image.save(img_path)

        # Retornar a imagem como um arquivo
        return send_file(img_path, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
