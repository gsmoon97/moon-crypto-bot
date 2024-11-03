from apscheduler.schedulers.background import BackgroundScheduler


class PurchaseScheduler:
    def __init__(self, upbit_api):
        self.scheduler = BackgroundScheduler()
        self.upbit_api = upbit_api

    def schedule_purchase(self, optimal_hours):
        for hour in optimal_hours:
            self.scheduler.add_job(self.upbit_api.buy_bitcoin, 'cron', hour=hour)
        self.scheduler.start()
