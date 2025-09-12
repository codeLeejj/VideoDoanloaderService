import os

from flask import Flask, request, jsonify, render_template
import logging
from datetime import datetime

import AddressHandler
from AddressHandler import AddressHandler, download_video

app = Flask(__name__)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


###################################### web start ###########################################
@app.route('/')
def index():
    try:
        path = "index.html"
        return render_template(path)
    except Exception as e:
        logger.error(e)
        return jsonify({
            "status": "success",
            "message": f"参数已接收并打印",
        }), 400


@app.route('/doc')
def doc():
    path = "doc.html"
    return render_template(path)


###################################### web end #############################################
@app.route('/print', methods=['GET', 'POST'])
def print_param():
    try:
        param = None
        source = ""

        # 从不同方式获取参数
        if request.method == 'GET':
            param = request.args.get('param')
            source = "GET query parameter"
        elif request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                param = data.get('param')
                source = "POST JSON body"
            else:
                param = request.form.get('param')
                source = "POST form data"

        if param:
            # 打印到控制台（会在docker logs中显示）
            print(f"[{datetime.now()}] 接收到参数: {param} (来自: {source})")
            logger.info(f"Received parameter: {param} from {source}")

            return jsonify({
                "status": "success",
                "message": f"参数已接收并打印",
                "received_param": param,
                "source": source,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "请提供参数。使用方式: ?param=value 或 JSON中的param字段"
            }), 400

    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "服务器内部错误"
        }), 500


@app.route('/query', methods=['GET', 'POST'])
def query():
    try:
        url = None
        source = ""

        # 从不同方式获取参数
        if request.method == 'GET':
            url = request.args.get('url')
            source = "GET query parameter"
        elif request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                url = data.get('url')
                source = "POST JSON body"
            else:
                url = request.form.get('url')
                source = "POST form data"

        if url:
            # 打印到控制台（会在docker logs中显示）
            formats = {}
            try:
                formats = AddressHandler().query(url)
            except Exception as e:
                logger.info({"code": -1, "message": f"{e}"})
            logger.info(f"获取的列表：{formats}")
            return jsonify(formats), 200
        else:
            return jsonify({
                "status": "error",
                "message": "请提供参数。使用方式: ?param=value 或 JSON中的param字段"
            }), 400

    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "服务器内部错误"
        }), 500


@app.route('/download', methods=['GET', 'POST'])
def download():
    get_sys_info()
    try:
        url = None
        param = None
        source = ""
        # 从不同方式获取参数
        if request.method == 'GET':
            url = request.args.get('url')
            param = request.args.get('param')
            source = "GET query parameter"
        elif request.method == 'POST':
            if request.is_json:
                data = request.get_json()
                url = data.get('url')
                param = data.get('param')
                source = "POST JSON body"
            else:
                url = request.form.get('url')
                param = request.form.get('param')
                source = "POST form data"
        logger.info(f"准备下载视频({source})：{param}  {url}")
        if url:
            result = download_video(url, param, "../media")
            logger.info(f"下载视频结果: {result}")
            return jsonify(result), 200
        else:
            return jsonify({
                "status": "error",
                "message": "请提供参数。使用方式: ?param=value 或 JSON中的param字段"
            }), 400


    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "服务器内部错误"
        }), 500


def get_sys_info():
    import platform
    import sys
    # 操作系统类型
    logger.info(f"操作系统:{platform.system()}")  # Windows, Linux, Darwin
    logger.info(f"操作系统版本:{platform.release()}")
    logger.info(f"操作系统详细信息:{platform.platform()}")
    print(f"操作系统版本号:{platform.version()}")

    # Python信息
    logger.info(f"Python版本:{sys.version}")
    logger.info(f"Python实现:{platform.python_implementation()}")  # CPython, PyPy等


if __name__ == '__main__':
    get_sys_info()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# if __name__ == "__main__":
#     downloader = AddressHandler()
#     _url = 'https://www.youtube.com/watch?v=QJkJMKqukwo'
#     download_video(_url, '137+251', "./media")
