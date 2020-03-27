from app import create_app

app = create_app('config.TestConfig')

if __name__ == '__main__':
    app.run()
