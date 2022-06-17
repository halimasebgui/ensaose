from contextlib import redirect_stderr
from fastapi import FastAPI, File, UploadFile, responses ,Request,Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pickle import TRUE
from pydoc import allmethods
import mysql.connector 
import numpy as np
import mysql.connector
import starlette.status as status
from fastapi.middleware.cors import CORSMiddleware
from pydoc import allmethods
import pytesseract
from pdf2image import convert_from_path
import os
import cv2
import xlrd 



app= FastAPI()

origins = [
   "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OV:
    ov_list = []

    def __init__(self, ov, page, status):
        self.ov = ov
        self.page = page
        self.status = status
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index1.html",{"request": request } )
@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    return templates.TemplateResponse("dashboard.html",{"request": request } )

@app.post("/")
async def resultat4(request: Request,email: str =Form(...),password: str =Form(...)):
   
    conn = mysql.connector.connect(host="localhost",
                                user="root",
                                password="", 
                                database="datasource")
    cursor = conn.cursor()
 
    sql_create="SELECT email, password from login"
    cursor.execute(sql_create) 
    resultat1 = cursor.fetchall()
    for vari in resultat1:

        if email==vari[:][0] and password==vari[:][1]:
                
            link = request.url_for("admin")
            return RedirectResponse(link,status_code=status.HTTP_302_FOUND)
        else:

            link = request.url_for("home")
            return RedirectResponse(link,status_code=status.HTTP_302_FOUND)
     #############virementttttttttt
@app.get("/admin/ocrOV", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html",{"request": request } )
    username = email
@app.post("/ocr/virement", response_class=HTMLResponse)
async def resultat(request: Request,uploaded_file: UploadFile = File(...)):
    ovs = exemple(uploaded_file)
    return templates.TemplateResponse("result.html",{"request": request,"listov":ovs})
def exemple(uploaded_file):
    file_location = f"static/{uploaded_file.filename}"
    with open(file_location, "wb+") as file_object: #ouvrir en ecriture
        file_object.write(uploaded_file.file.read())
    #return {"info": f"file '{uploaded_file.filename}' saved at '{file_location}'"}
    
    # Store Pdf with convert_from_path function
    images = convert_from_path(file_location,poppler_path=r"C:\poppler-22.04.0\Library\bin")


    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save('static/page' + str(i) + '.jpg', 'JPEG')


    template = cv2.imread("template.jpg", 0)
    # cv2.imshow("Template", template)
    # cv2.waitKey()

    orders = []
    OV.ov_list=[]
    counter = 0
    for filename in os.listdir("."):
        if filename.endswith(".jpg"):
            if "page" in filename:
                frame = cv2.imread(f"{filename}", 0)
                result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)

                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result, None)
                counter += 1
                # print(counter)
                # print(min_loc, max_loc)
                # print(template.shape[0], template.shape[1])

                cropped = frame[
                    max_loc[1] + 34  : max_loc[1] + template.shape[0]   ,      #haut+ bas- deduire
                    max_loc[0] : max_loc[0] + template.shape[1]    ,       #largeur_droite+ deduire
                ]

                #cv2.imshow("Cropped", cropped)
                #cv2.waitKey()
                elem=int(pytesseract.image_to_string(cropped))
                try:
                    orders.append(int(pytesseract.image_to_string(cropped)))
                    
                    # valide (ov,page, valide)
                    OV.ov_list.append(OV(elem, counter, 'valide'))
                except:
                    # invalide (null, page, invalide)
                    OV.ov_list.append(OV(elem, counter, 'invalide'))
                    pass
    nums  = []
    for elem in orders:
        try:
            nums.append(str(elem) +'/2020')
        except:
            pass
    print(nums)
    t = tuple(nums)
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="virement"
    )

    mycursor = mydb.cursor()

    sql = "UPDATE virements SET valide = 1 WHERE id_virement IN  {}".format(t)
    #sql= "SELECT * FROM virements"
    mycursor.execute(sql)

    mydb.commit()

    print(mycursor.rowcount, "record(s) affected")
    return OV.ov_list
        

        #####bnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
@app.get("/admin/ocrBC", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("bc.html",{"request": request } )

@app.post("/ocr/bc", response_class=HTMLResponse)
async def resultat(request: Request,uploaded_file: UploadFile = File(...)):
    ovs = exemple1(uploaded_file)
    return templates.TemplateResponse("result1.html",{"request": request,"listbc":ovs})

def exemple1(uploaded_file):
    file_location = f"static/{uploaded_file.filename}"
    with open(file_location, "wb+") as file_object: #ouvrir en ecriture
        file_object.write(uploaded_file.file.read())
    #return {"info": f"file '{uploaded_file.filename}' saved at '{file_location}'"}

    # Store Pdf with convert_from_path function
    images = convert_from_path(file_location,poppler_path=r"C:\poppler-22.04.0\Library\bin")

    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save('static/feuille' + str(i) + '.jpg', 'JPEG')

    template = cv2.imread("static\F.jpg", 0)
    # cv2.imshow("Template", template) 
    # cv2.waitKey()

    orders = []
    OV.ov_list=[]
    counter = 0
    for filename in os.listdir("."):
        if filename.endswith(".jpg"):
            if "feuille" in filename:
                frame = cv2.imread(f"{filename}", 0)
                result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)

                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result, None)
                counter += 1
                # print(counter)
                # print(min_loc, max_loc)
                # print(template.shape[0], template.shape[1])

                cropped = frame[
                    max_loc[1] : max_loc[1] + template.shape[0] -68 ,      #haut+ bas- deduire
                    max_loc[0] +278 : max_loc[0] + template.shape[1]   ,         #largeur_droite+ deduire
                ]

                #cv2.imshow("Cropped", cropped)
                #cv2.waitKey()
                # try:
                #     orders.append(int(pytesseract.image_to_string(cropped)))
                # except:
                #     pass
                elem=int(pytesseract.image_to_string(cropped))
                try:
                    orders.append(int(pytesseract.image_to_string(cropped)))
                    
                    # valide (ov,page, valide)
                    OV.ov_list.append(OV(elem, counter, 'valide'))
                except:
                    # invalide (null, page, invalide)
                    OV.ov_list.append(OV(elem, counter, 'invalide'))
                    pass
    # nums  = []
    # for elem in orders:
    #     try:
    #         nums.append(str(elem) +'/2020')
    #     except:
    #         pass
   # print(orders)

    t = tuple(orders)
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="datasource"
    )

    mycursor = mydb.cursor()

    sql = "UPDATE engagements SET valide = 1 WHERE id IN  {}".format(t)
    #sql= "SELECT * FROM virements"
    mycursor.execute(sql)

    mydb.commit()

    print(mycursor.rowcount, "record(s) affected")
    return  OV.ov_list

#####budgeeeeeeettttttttttttttttttt

@app.get("/admin/budget", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("budget.html",{"request": request } )
@app.post("/budget/bud", response_class=HTMLResponse)
async def resultat(request: Request,uploaded_file: UploadFile = File(...)):
    list1 = up(uploaded_file)
    return templates.TemplateResponse("resultt.html",{"request": request,"list1":list1})
    return templates.TemplateResponse("resultt.html",{"request": request})

def up(uploaded_file):
    file_location = f"static/{uploaded_file.filename}"
    with open(file_location, "wb+") as file_object: #ouvrir en ecriture
        file_object.write(uploaded_file.file.read())

    workbook = xlrd.open_workbook(file_location)
    SheetNameList = workbook.sheet_names()
    for i in np.arange( len(SheetNameList) ):
        print( SheetNameList[i] )
    worksheet = workbook.sheet_by_name(SheetNameList[0])
    num_rows = worksheet.nrows 
    num_cells = worksheet.ncols 
    lit2=[]


    
    credit=[]
    curr_row = 2
    while curr_row < num_rows:
        list1=[]
        row = worksheet.row(curr_row)
        
        num=5
        curr_cell = 0
        while curr_cell < num:
        
            cell_type = worksheet.cell_type(curr_row, curr_cell)
            cell_value = worksheet.cell_value(curr_row, curr_cell)
            curr_cell += 1
            if curr_cell == 4:
                continue
            if curr_cell < 4:
                cell= cell_value.split(",")
                cell_value=cell[0]
            list1.append(cell_value)  
        curr_row += 1
        lit2.append(list1)
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="datasource"
    )
    mycursor = mydb.cursor()
    taille=len(lit2)
    litstim=[]
    budgett=[]
    for n in lit2: 
        chap=lit2[taille-1][0].split(":")
        chaine=chap[1]+" -"+n[0]+"- "+ n[1]+"- "+ n[2]
        #print(imputation)
        imputation=chaine.lstrip()
        bud=n[3]
        #if "Total" not in imputation  : 
        #if isinstance( n[2], (int, float)) :
        #if  bud is not None:
             #litstim.append(imputation)
        if bud !='' and bud!='______' and "Total" not in imputation  and n[2].isdigit() : 
             budgett.append(bud)
             litstim.append(imputation)
             sql = "UPDATE imputation SET budget = %s WHERE imputation = %s" 
             mycursor.execute(sql,(bud,imputation,))
             mydb.commit()   
        print(mycursor.rowcount, "record(s) affected")
    #print(budgett) 
    #print(litstim)  
    
    conn = mysql.connector.connect(host="localhost",
                                user="root", password="", 
                                database="datasource")
    cursor = conn.cursor()
    list1=[]
    list2=[]
    list3=[]
    list4=[]
    
    sql_create="SELECT imputation_id ,budget,sum(montant) ,budget-sum(montant)  as dispo from engagements e INNER JOIN imputation i WHERE i.imputation=e.imputation_id GROUP BY imputation_id"
    cursor.execute(sql_create)
    resultat1 = cursor.fetchall()
    for utilisateur1 in resultat1:
        
            list1.append(utilisateur1)
                
    #print(list2)
    #print(list3)
    #print(list4)
    conn.close()
    #print(list1)
    return list1
        






    


# from pickle import TRUE
# from pydoc import allmethods
# from pandas import notnull
# import xlrd 
# #from openpyxl import workbook 
# #from openpyxl import load_workbook
# import numpy as np
# import mysql.connector 
# from fastapi import FastAPI, File, UploadFile, responses ,Request
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles

# app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")
# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     list = afficher()
#     return templates.TemplateResponse("users.html",{"request": request ,"list":list} )
# async def afficher():
#      conn = mysql.connector.connect(host="localhost",
#                                 user="root",
#                                 password="", 
#                                 database="datasource")
#      cursor = conn.cursor()
 
#      sql_create="SELECT user-name,email from login"
#      cursor.execute(sql_create) 
#      resultat1 = cursor.fetchall()
#      list=[]
#      for vari in resultat1:
#         list.append(vari)
#         print(vari)
#      conn.close()
#      return list    


        
      






        






  

