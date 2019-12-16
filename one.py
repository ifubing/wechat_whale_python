import flask
import flask_script
import hashlib

app = flask.Flask(__name__)
app.config['DEBUG'] = True

manager = flask_script.Manager(app)
WECHAT_TOKEN = 'pyhui'


@app.route('/')
def index():
    return '微信公众号测试主页'


import random
def get_weather():
    weahter_list = ['晴天','雨天','阴天','晴转多云']
    return random.choice(weahter_list)


@app.route('/wechat',methods=['GET','POST'])
def wechat():
    """对接微信公众号服务器"""
    print('in wechat')
    # 接收微信服务器发来的参数
    signature = flask.request.args.get("signature")
    timestamp = flask.request.args.get("timestamp")
    nonce = flask.request.args.get("nonce")
    # echostr = flask.request.args.get("echostr")

    # 校验参数
    # if not all([signature, timestamp, nonce, echostr]):
    if not all([signature, timestamp, nonce]):
        flask.abort(400)

    # 按照微信的流程进行计算签名
    li = [WECHAT_TOKEN, timestamp, nonce]
    # 排序
    li.sort()
    # 拼接字符串
    tmp_str = "".join(li)
    # 进行sha1加密，得到签名值
    sign = hashlib.sha1(tmp_str.encode()).hexdigest()
    # 将得到的签名值与请求的参数对比
    if signature != sign:
        flask.abort(403)
    else:
        # 如果是验证身份
        if flask.request.method == 'GET':
            echostr = flask.request.args.get("echostr")
            return echostr
        # 如果是发送消息
        elif flask.request.method == 'POST':
            print('进入post请求')
            xml_str = flask.request.data
            import xmltodict
            xml_dict = xmltodict.parse(xml_str)
            xml_dict = xml_dict.get('xml')

            # 提取类型与内容
            msg_type = xml_dict.get('MsgType')
            print('请求类型为', msg_type)

            import time
            # 类型判断
            if msg_type == 'text':

                if xml_dict.get('Content') == '天气':
                    content = get_weather()
                else:
                    content = '不存在的服务'
                # 构建返回的字典
                resp_dict = {
                    'xml': {
                        'ToUserName': xml_dict.get('FromUserName'),
                        'FromUserName': xml_dict.get('ToUserName'),
                        'CreateTime': int(time.time()),
                        'MsgType': 'text',
                        # 'Content': xml_dict.get('Content')
                        'Content': content
                    }
                }


                # 字典转 xml
                resp_xml_str = xmltodict.unparse(resp_dict)
                print('返回内容为',resp_xml_str)
                return resp_xml_str




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)