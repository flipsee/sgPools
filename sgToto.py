import sgPoolsModel

import logging

import base64
import dateutil
import dateutil.parser
from datetime import timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup
from array import array

logger = logging.getLogger("sgPools.sgTotoResult")

def encode(word): 
    return base64.b64encode(word.encode())

def CreateCombo(arr, k):
    ret = []
    i = 0
    for var1 in arr:
        if k == 1: #last item
            ret.append([str(arr[i]).zfill(2)])
            #print("k: " + str(k) +  ";i: " + str(i) + ";arr[i]: " + str(arr[i]))
        else:
            sub = CreateCombo(arr[i+1:len(arr)], k-1)
            #print("sub: " + str(sub))

            x = 0
            for var2 in sub:
                next = sub[x]
                next.insert(0,str(arr[i]).zfill(2))
                ret.append(next)
                x+=1
        i += 1
    return ret

def CreateAllCombination(list,k):
    list.sort()
    ret = []
    for i in range(1,k+1):
        ret += CreateCombo(list,i)
    return ret


class TotoResult:
    def __init__(self,url=None):        
        if url is None:
            self.url = "http://www.singaporepools.com.sg/en/product/sr/Pages/toto_results.aspx?"
        else:
            self.url = url
            
    def getTOTOQueryString(self, word):
        encoded = encode(word)
        return "sppl=" + encoded.decode("utf-8")
    
    def getTotoResults(self, DrawNumber):
        _result = {}
        logger.info("Getting Toto Result Draw No: " + str(DrawNumber))

        try:
            queryString = self.getTOTOQueryString("DrawNumber=" + str(DrawNumber))
            logger.info(self.url + queryString)  
            
            page = urlopen(self.url + queryString)           
            soup = BeautifulSoup(page, 'html.parser')
            
            ### Get Results ###
            data = {}
            drawNumber = soup.find('th', attrs={'class': 'drawNumber'})
            data['DrawNumber'] = drawNumber.text.strip().replace("Draw No. ","")

            drawDate = soup.find('th', attrs={'class': 'drawDate'})
            logger.info("Draw Date: " + str(drawDate.text.strip()))
            data['DrawDate'] = dateutil.parser.parse(drawDate.text.strip())

            win1 = soup.find('td', attrs={'class': 'win1'})
            data['Win1'] = int(win1.text.strip())
            
            win2 = soup.find('td', attrs={'class': 'win2'})
            data['Win2'] = int(win2.text.strip())
            
            win3 = soup.find('td', attrs={'class': 'win3'})
            data['Win3'] = int(win3.text.strip())
            
            win4 = soup.find('td', attrs={'class': 'win4'})
            data['Win4'] = int(win4.text.strip())
            
            win5 = soup.find('td', attrs={'class': 'win5'})
            data['Win5'] = int(win5.text.strip())
            
            win6 = soup.find('td', attrs={'class': 'win6'})
            data['Win6'] = int(win6.text.strip())           
            
            #winningNumbers = array("i")
            #winningNumbers.append(int(win1.text.strip()))
            #winningNumbers.append(int(win2.text.strip()))
            #winningNumbers.append(int(win3.text.strip()))
            #winningNumbers.append(int(win4.text.strip()))
            #winningNumbers.append(int(win5.text.strip()))
            #winningNumbers.append(int(win6.text.strip()))
            #data['winningNumbers'] = winningNumbers

            additionalNumber = soup.find('td', attrs={'class': 'additional'})
            data['AdditionalNumber'] = int(additionalNumber.text.strip())

            data['QueryString'] = queryString

            _result = data
        except Exception as ex:
            logger.info("Processing Error, Draw Number: " + str(DrawNumber) + ", Record Skipped")
            logger.error(ex, exc_info=True)
            #raise
        finally:
            if _result['DrawNumber'] is None:
                _result['Status'] = False
            else:
                if (_result['DrawNumber'] == str(DrawNumber)):
                    _result['Status'] = True
                else:
                    _result['Status'] = False
            return _result

    def refreshTotoResult(self, DrawNumber, ThrowError=False):
        try:
            jsonObj = self.getTotoResults(DrawNumber)
            if jsonObj == []:
                pass
            else:
                if jsonObj["Status"] == True:
                    data = sgPoolsModel.sgPoolsBL()
                    try:
                        with data.atomic() as txn:
                            data.add_dicttotoresult(jsonObj)
                    except ValueError:
                        pass
                    finally:
                        data.close()
                else:
                    logger.info("Draw Number: " + str(DrawNumber) + " Get Status: " + str(jsonObj["Status"]))
        except Exception as ex:
            logger.info("Draw Number: " + str(DrawNumber) + " Error. Failed to enter to DB, record skipped ")
            logger.error(ex, exc_info=True)
            data = sgPoolsModel.sgPoolsBL()
            try:
                with data.atomic() as txn:
                    data.add_Failedtotoresult(DrawNumber)
            except ValueError:
                pass
            finally:
                data.close()
            
            if ThrowError:
                raise
            

    def refreshTotoResults(self, StartDrawNumber, EndDrawNumber):
        count = 0
        try:
            logger.info("Getting Toto Results From: " + str(StartDrawNumber) + "-" + str(EndDrawNumber))            

            for num in range(StartDrawNumber,EndDrawNumber + 1):
                self.refreshTotoResult(num)
                count += 1

            logger.info("Completed Getting Results, Count: " + str(count))
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise

    def clearTotoResults(self):
        data = sgPoolsModel.sgPoolsBL()
        try:
            with data.atomic() as txn:
                data.clear_totoresults()
        except:
            logger.error(ex, exc_info=True)
            raise
        finally:
            data.close()

    def refreshFailedTotoResults(self): 
        count = 0
        try:
            data = sgPoolsModel.sgPoolsBL()
            with data.atomic() as txn:
                temp = list(data.get_failedtotoresult())
            data.close()

            for num in temp:
                try:
                    logger.info("Draw Number: " + str(num.DrawNumber) + " Processing")

                    self.refreshTotoResult(num.DrawNumber, True)
                    
                    data = sgPoolsModel.sgPoolsBL()
                    try:
                        with data.atomic() as txn:
                            data.delete_failedtotoresult(num.DrawNumber)
                    except:
                        pass
                    finally:
                        data.close()

                    count += 1
                except Exception as ex:
                    logger.info("Draw Number: " + str(num.DrawNumber) + " Error")
                    logger.error(ex, exc_info=True)
            logger.info("Completed RefreshingFailed Toto Result, Count: " + str(count))
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise

    def calculateDrawDate(self, DrawNumber):
        result = dateutil.parser.parse('2001-Jan-01')
        anchorDrawNumber = 1200
        anchorDrawDate = dateutil.parser.parse('1997-Jul-24') #this is Thursday
    
        try:
            #1. calculate how many draw passed since the anchor Draw Num.
            drawDistanceToAnchor = DrawNumber - anchorDrawNumber

            #2. calculate how many weeks passed based to the drawNumber
            weekdistanceToAnchor = int(drawDistanceToAnchor/2) #have 2 draw(Mon, Thu) in a week.

            #3. calculate how many days passed based to the drawNumber
            if drawDistanceToAnchor < 0 and drawDistanceToAnchor%2 > 0:
                daysdistanceToAnchor = (weekdistanceToAnchor * 7) - 3 #distance from Thursday to prev Monday = 3 days. (this is because our anchor is Thursday)
            elif drawDistanceToAnchor > 0 and drawDistanceToAnchor%2 > 0:
                daysdistanceToAnchor = (weekdistanceToAnchor * 7) + 4 #distance from Thursday to next Monday = 4 days. (this is because our anchor is Thursday)
            else:
                daysdistanceToAnchor = (weekdistanceToAnchor * 7)

            result = anchorDrawDate + timedelta(days=(daysdistanceToAnchor))

            #print(str(drawDistanceToAnchor))
            #print(str(drawDistanceToAnchor/2))
            #print(str(weekdistanceToAnchor))
            #print(str(drawDistanceToAnchor%2))
            #print(str(daysdistanceToAnchor))
        except Exception as ex:
            pass
        finally:
            return result

    def updateOldTotoDrawDate(self):
        try:
            start_DrawNumber = 999
            end_DrawNumber = 1194
            for num in range(start_DrawNumber, end_DrawNumber):
                drawDate = self.calculateDrawDate(num)
                data = sgPoolsModel.sgPoolsBL()
                try:
                    with data.atomic() as txn:
                        logger.info("DrawNumber: " + str(num) + " DrawDate: " + str(drawDate))
                        data.update_totodrawdate(num, drawDate)
                except Exception as ex:
                    logger.error(ex, exc_info=True)
                    raise
                finally:
                    data.close()            
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise

    def ProcessTotoResult(self, **kwargs):
        DrawNumber = kwargs.get('DrawNumber', None)
        MaxCombinationLength = 7
        count = 0
        try:
            data = sgPoolsModel.sgPoolsBL()
            with data.atomic() as txn:
                if DrawNumber is None:
                    temp = list(data.get_totoresults())
                else:
                    temp = [data.get_totoresult(DrawNumber)]
            data.close()
            
            for num in temp:
                try:
                    logger.info("Draw Number: " + str(num.DrawNumber) + " Processing")                  
                    DrawNumbers = []
                    DrawNumbers.append(num.Win1)
                    DrawNumbers.append(num.Win2)
                    DrawNumbers.append(num.Win3)
                    DrawNumbers.append(num.Win4)
                    DrawNumbers.append(num.Win5)
                    DrawNumbers.append(num.Win6)
                    DrawNumbers.append(num.AdditionalNumber)                    
                    #logger.info("Draw Number: " + str(num.DrawNumber) + " DrawNumbers: " + str(DrawNumbers))

                    result = CreateAllCombination(DrawNumbers,MaxCombinationLength)

                    temp = []
                    for item in result:
                        temp2 = {}
                        temp2['DrawNumber'] = num.DrawNumber
                        temp2['CombinationNumber'] = ','.join(item)
                        temp.append(temp2)
                    #logger.info("Result: " + str(result))

                    data = sgPoolsModel.sgPoolsBL()
                    try:
                        with data.atomic() as txn:
                            data.add_processedtotoresults(temp)
                            count += 1
                    except Exception as ex:
                        logger.error(ex, exc_info=True)
                        pass
                    finally:
                        data.close()
                    #for item in result:
                    #    try:
                    #        with data.atomic() as txn:
                    #            data.add_processedtotoresult(','.join(item), num.DrawNumber)
                    #            logger.info("Draw Number: " + str(num.DrawNumber) + " Combo:" + ','.join(item))
                    #            count += 1
                    #    except Exception as ex:
                    #        logger.error(ex, exc_info=True)
                    #        pass
                    #    finally:
                    #        data.close()
                except Exception as ex:
                    #logger.info("Draw Number: " + str(num.DrawNumber) + " Error")
                    logger.error(ex, exc_info=True)
                #break
            #logger.info("Completed RefreshingFailed Toto Result, Count: " + str(count))         
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise

    def getGroupedTotoResult(self):
        strTemplate = "result.push({{CombinationNumber: '{0}', DrawNumber: [{1}]}});"
        try:
            with open('toto_result.js', 'w') as file:
                file.write("var result = [];" + "\n")

            data = sgPoolsModel.sgPoolsBL()
            try:
                with data.atomic() as txn:
                    temp = list(data.get_groupedtotoresult())
                    for num in temp:
                        #logger.info("Combination Number: " + str(num.CombinationNumber) + " Draw Numbers: " + str(num.DrawNumber))
                        #logger.info(strTemplate.format(str(num.CombinationNumber),str(num.DrawNumber)))
                        with open('toto_result.js', 'a') as file:
                            file.write(strTemplate.format(str(num.CombinationNumber),str(num.DrawNumber)) + "\n")
            except:
                pass
            finally:                
                data.close()
        except Exception as ex:
            logger.error(ex, exc_info=True)
            raise
