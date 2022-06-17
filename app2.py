from pickle import TRUE
from pydoc import allmethods
from pandas import notnull
import xlrd 
#from openpyxl import workbook 
#from openpyxl import load_workbook
import numpy as np
import mysql.connector 
from fastapi import FastAPI, File, UploadFile, responses ,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app2 = FastAPI()
app2.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
@app2.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html",{"request": request } )

@app2.post("/budget/bud", response_class=HTMLResponse)
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
        