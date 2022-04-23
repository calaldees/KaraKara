from sanic import Sanic, response

app = Sanic("karakara_queue")
#app.ctx.db = Database()

@app.get("/")
def basic(request):
    return response.text("foo")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337, workers=4)
