import logging
import sgToto

import sgPoolsModel

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

toto = sgToto.TotoResult()

#start_DrawNumber = 999
#end_DrawNumber = 3324

#data = sgPoolsModel.sgPoolsBL()
#try:
#    for num in range(start_DrawNumber, end_DrawNumber):
#        drawData = data.get_totoresult(num)
#        if drawData is None:
#            logging.info(num)
#except ValueError:
#    pass
#finally:
#    data.close()
#    logging.info("looping completed.")


#toto.refreshTotoResults(start_DrawNumber, end_DrawNumber)
#toto.refreshFailedTotoResults()

#toto.refreshTotoResult(1197)
#toto.refreshTotoResult(1220)
#toto.refreshTotoResult(1232)
#toto.refreshTotoResult(1266)
#toto.refreshTotoResult(3347)

#print(str(toto.calculateDrawDate(1199)))
#toto.updateOldTotoDrawDate()
toto.ProcessTotoResult(DrawNumber=3347)
#toto.getGroupedTotoResult()
