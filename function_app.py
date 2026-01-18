import azure.functions as func
import logging
from sharepoint_integration.sharepoint_sam import main

app = func.FunctionApp()

@app.timer_trigger(schedule="0 0 */6 * * *", 
                   arg_name="myTimer", 
                   run_on_startup=False)
def scheduled_sync(myTimer: func.TimerRequest) -> None:
    logging.info('Starting SharePoint sync...')
    try:
        main()
        logging.info('Sync completed successfully')
    except Exception as e:
        logging.error(f'Sync failed: {str(e)}')
        raise
