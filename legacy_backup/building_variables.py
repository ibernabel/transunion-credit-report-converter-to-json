import pandas as pd
import json
#import re
#with open("./output_text/idequel.txt", "r") as file:
#    content = file.read()

file = open("./output_text/idequel.txt", "r")

text = file.read()

rnc_index = text.find("rnc")

#Defautl variables
score = "No score"
scoring = "No score"
summary_of_open_accounts_text = "No summary"
summary_of_open_accounts_end = "No summary"

#inquirer data indexes
subscriber_index = text.find("suscriptor:")
user_index = text.find("usuario:")
consultation_date_index = text.find("fecha:")
consultation_time_index = text.find("hora:")

#inquirer variables
inquirer = {}
subscriber = text[subscriber_index + 12 : user_index -1]
user = text[user_index + 9 : consultation_date_index - 1]
consultation_date = text[consultation_date_index + 7 : consultation_time_index -1]
consultation_time = text[consultation_time_index + 6 : consultation_time_index +14]
inquirer.update({"suscriptor": subscriber, "usuario": user, "fecha consulta": consultation_date, "hora consulta":consultation_time })

print('[')
json_inquirer = json.dumps(inquirer)
print(f'{{"inquirer": {json_inquirer}}},\n')

#Define type of Credit Report
is_individual_credit_history_type = text.find("historia de credito de individuo") != -1
is_transunion_credit_vision_score_type = text.find("transunion credit vision score") != -1

if is_transunion_credit_vision_score_type:
  reporting_type = "Transunion Credit Vision Score"
else:
  reporting_type = "Historia De Crédito De Individuo"

#Define which Headings contains it

#transunion_creditvision_score_table
has_transunion_creditvision_score_table = False
if is_transunion_credit_vision_score_type:
  has_transunion_creditvision_score_table = True
  transunion_creditvision_score_table_index = text.find("transunion creditvision score")

#resumen_de_cuentas_abiertas_table
has_resumen_de_cuentas_abiertas_table = text.find("resumen de cuentas abiertas") != -1
resumen_de_cuentas_abiertas_table_index = text.find("resumen de cuentas abiertas")

#detalle_de_cuentas_abiertas_table
has_detalle_de_cuentas_abiertas_table = text.find("detalle de cuentas abiertas") != -1
detalle_de_cuentas_abiertas_table_index = text.find("detalle de cuentas abiertas")

#leyenda_comportamiento_historico
has_leyenda_comportamiento_historico_title = text.find("leyenda comportamiento historico") != -1
leyenda_comportamiento_historico_index = text.find("leyenda comportamiento historico")

#resumen_de_cuentas_abiertas_table
has_detalle_de_cuentas_cerradas_inactivas_table = text.find("detalle de cuentas cerradas / inactivas") != -1
detalle_de_cuentas_cerradas_inactivas_table_index = text.find("detalle de cuentas cerradas / inactivas")

#indagaciones_ultimos_6_meses_table
has_indagaciones_ultimos_6_meses_table = text.find("indagaciones ultimos 6 meses") != -1
indagaciones_ultimos_6_meses_table_index = text.find("indagaciones ultimos 6 meses")

#datos_personales_table and index
has_datos_personales_table = text.find("datos personales") != -1
datos_personales_table_index = text.find("datos personales")
identification_index = text.find("cedula")
names_index = text.find("nombres")
lastnames_index = text.find("apellidos")
birthday_index = text.find("fecha nacimiento")
age_index = text.find("edad")
ocupation_index = text.find("ocupacion")
place_of_birth_index = text.find("lugar nacimiento")
passport_index = text.find("pasaporte")
marital_status_index = text.find("estado civil")
phones_index = text.find("telefonos")
home_phone_index = text.find("casa:")
work_phone_index = text.find("trabajo:")
personal_phone_index = text.find("celular:")
addresses_index_start = text.find("direcciones")

#Define the end of the addresses line
if has_transunion_creditvision_score_table:
  addresses_index_end = transunion_creditvision_score_table_index - 1
elif has_resumen_de_cuentas_abiertas_table:
  addresses_index_end = resumen_de_cuentas_abiertas_table_index - 1
elif has_detalle_de_cuentas_cerradas_inactivas_table:
  addresses_index_end = detalle_de_cuentas_cerradas_inactivas_table_index - 1
else:
  addresses_index_end = indagaciones_ultimos_6_meses_table_index - 1
  
#personal data variables:
personal_data = {}
identification = text[identification_index + 8 : identification_index + 21]
names = text[names_index + 8 : lastnames_index - 1]
lastnames = text[lastnames_index + 10 : birthday_index - 1]
birthday = text[birthday_index + 17 : age_index - 1]
age = text[age_index + 5 : age_index + 7]
ocupation = text[ocupation_index + 10 : place_of_birth_index - 1]
place_of_birth = text[place_of_birth_index + 17 : passport_index - 1]
passport = text[passport_index + 10 : marital_status_index - 1]
marital_status = text[marital_status_index + 13 : phones_index - 1]
phones = {}
home_phone = text[home_phone_index + 6 : work_phone_index - 1]
work_phone = text[work_phone_index + 9 : personal_phone_index - 1]
personal_phone = text[personal_phone_index + 9 : addresses_index_start - 1]
phones.update({"casa": home_phone, "trabajo": work_phone, "celular": personal_phone})
addresses_raw = text[addresses_index_start + 12 : addresses_index_end]
addresses_raw = addresses_raw.split('* ')
addresses_raw.pop(0)
addresses =[]

for address in addresses_raw:
    address = address.rstrip('\n').replace('\n', ' ')
    addresses.append(address)
    
personal_data.update({"cedula": identification, "nombres": names, "apellidos": lastnames, "fecha nacimiento": birthday, "edad": age, "ocupacion": ocupation, "lugar nacimiento": place_of_birth, "pasaporte": passport, "estado civil": marital_status, "telefonos": phones, "direcciones": addresses})

json_personal_data = json.dumps(personal_data)
print(f'{{"personal_data": {json_personal_data}}},\n')

#credit vision table
has_transunion_creditvision_score_table = True
transunion_creditvision_score_table_index = text.find("transunion creditvision score")

if has_transunion_creditvision_score_table:
  puntuacion_index = text.rfind("puntuacion")
  score = text[puntuacion_index +10 : puntuacion_index + 14] 
  factors_index = text.find("factores")  
  factors = text[factors_index + 36 : rnc_index - 1]
  factors = factors.replace('* ', '').replace(') ', ')').split('\n')

#building summary open accounts table

if has_resumen_de_cuentas_abiertas_table:
  if has_leyenda_comportamiento_historico_title:
    resumen_de_cuentas_abiertas_table_index_end = leyenda_comportamiento_historico_index - 1
  else:
    resumen_de_cuentas_abiertas_table_index_end = detalle_de_cuentas_abiertas_table_index - 1
  
  #Get the slice of text about open account summary
  resumen_de_cuentas_abiertas_table_text = text[resumen_de_cuentas_abiertas_table_index + 28 : resumen_de_cuentas_abiertas_table_index_end]
  #Making a list of each data split it of \n
  summary_of_open_accounts_list = resumen_de_cuentas_abiertas_table_text.split('\n')
  #Index where the each headers of de table ends(From Suscriber to % Utilitation):
  first_subscriber_row_start_index = 17 
  last_subscriber_row_end_index = summary_of_open_accounts_list.index("total general >>")
  #Split the data according to a table columns(11) from text list. Each 11 items is a row data
  data_rows_summary_account = [summary_of_open_accounts_list[i:i+11] for i in range(first_subscriber_row_start_index,last_subscriber_row_end_index, 11)]
  #print(len(data_rows_summary_account))
  #for row in data_rows_summary_account:
  #  print(row)

  #Making a dictionary from the rows data. Assigning each row to a dicctionary keys
  summary_open_accounts = [
		{
			"subscriber": row[0],
			"accounts_amount": row[1],
			"account_type": row[2],
			"credit_amount_dop": row[3],
			"credit_amount_usd": row[4],
			"current_balance_dop": row[5],
			"current_balance_usd": row[6],
			"current_overdue_dop": row[7],
			"current_overdue_usd": row[8],
			"utilization_percent_dop": row[9],
			"utilization_percent_usd": row[10],
		}
		for row in data_rows_summary_account
	]
json_summary_open_accounts = json.dumps(summary_open_accounts)
print(f'{{"summary_open_accounts": {json_summary_open_accounts}}},\n')
  #datable = pd.DataFrame(summary_open_accounts)
  ##print(datable.info())
  ##print(datable.describe())
  #print(datable)

#building DETAILS open accounts table 
if has_detalle_de_cuentas_abiertas_table:
  if has_detalle_de_cuentas_cerradas_inactivas_table:
    detalle_de_cuentas_abiertas_table_index_end = detalle_de_cuentas_cerradas_inactivas_table_index - 1
  else:
     detalle_de_cuentas_abiertas_table_index_end = indagaciones_ultimos_6_meses_table_index - 1
  
  #Get the slice of text about open account detils
  detalle_de_cuentas_abiertas_table_text = text[detalle_de_cuentas_abiertas_table_index + 28 : detalle_de_cuentas_abiertas_table_index_end]
  #Making a list of each data split it of \n
  details_of_open_accounts_list = detalle_de_cuentas_abiertas_table_text.split('\n')
  first_subscriber_row_start_index = 26 #Index where the each headers of de table ends
  last_subscriber_row_end_index = details_of_open_accounts_list.index("totales generales rd$:")
  # Selecting only the elments with information details not the headers
  details_of_open_accounts_list_data_rows = details_of_open_accounts_list[first_subscriber_row_start_index:last_subscriber_row_end_index]
  #print(details_of_open_accounts_list)
  #print(details_of_open_accounts_list_data_rows)

  # Processing the table rows for divide the information based in each suscriber data
  details_of_open_accounts_list_suscribers_rows = []
  sublista_actual = []  # Inicializar una sublista vacía

  #Function processe data into details open account
  #Split each suscriber data by ">>" character
  # Separate the data in the suscriber element of account type and suscriber name
  # Add each row modifyed to the final datatable
  def process_table_details_account(sublista_actual):
    suscriptor = [sublista_actual[0]]
    #Separar la informacion del tipo de cuenta y el suscriptor por los caracteres ">>"
    suscriptor = suscriptor[0].split(">>")

    #Eliminar los espacios en blanco que tengan al principio y al fimal
    for i in range (len (suscriptor)):
      suscriptor[i] = suscriptor[i].strip()
    # Crear las subsecuentes sublistas
    sublistas_resto = [sublista_actual[i:i+11] for i in range(1, len(sublista_actual), 11)]

    #Agregar el suscriptor a cada sublista (The data for each suscriber individualy)
    sublista_con_suscriptor_agregado = []

    for element in sublistas_resto:
      element = suscriptor + element
      sublista_con_suscriptor_agregado.append(element)

    # Creating the final datatable with each row proccesed (suscriber and account type added)
    for element in sublista_con_suscriptor_agregado:
      details_of_open_accounts_list_suscribers_rows.append(element)
  #End of function
   
    
  ##### Iterar a través de la lista original
  #_process_accounts_details_rows>>>>>>>>>>>
  for elemento in details_of_open_accounts_list_data_rows:

    if ">>" in elemento:
      # Si encontramos ">>", guardamos la sublista actual y creamos una nueva
      if sublista_actual:
        process_table_details_account(sublista_actual)
        sublista_actual = []

    ### NO TOCAR PROXIMA LINEA
    sublista_actual.append(elemento)  # Agregar elementos a la sublista actual

  # Agregar la última sublista a la lista final
  if sublista_actual:
    process_table_details_account(sublista_actual)
    sublista_actual = [] 

  print(f'\n\n\n 256:Details: {len(details_of_open_accounts_list_data_rows)}\n\n\n')
  #print(f'\n\n\n Details: {len(details_of_open_accounts_list_suscribers_rows)}\n\n\n')
  
  #Turn the 12 month behavior vector in a list
  for element in details_of_open_accounts_list_suscribers_rows:
    caracteres = element[12].replace(" ","")
    lista_resultante = [int(caracter) if caracter.isdigit() else None for caracter in caracteres]

    element[12] = lista_resultante
####___process_accounts_details_rows^^^^^^^^^^^^
  print(f'\n\n\n 266:Details: {len(details_of_open_accounts_list_suscribers_rows)}\n\n\n')
  #print("\n\n\n\n")
  #for row in details_of_open_accounts_list_suscribers_rows:
  #  print(len(row))
  #  print(row)
  #print("\n\n\n\n")

  details_open_accounts = [
		{
			"account_type": row[0],
			"subscriber": row[1],
			"status": row[2],
			"update_date": row[3],
			"opening_date": row[4],
			"expiration_date": row[5],
			"currency": row[6],
			"credit_limit": row[7],
			"current_balance": row[8],
			"balance_in_arrears": row[9],
			"minimum_payment_and_installment": row[10],
			"no_of_installments_and_modality": row[11],
			"behavior_vector_last_12_months": row[12],
		}
		for row in details_of_open_accounts_list_suscribers_rows
	]
  
json_details_open_accounts = json.dumps(details_open_accounts)
print(f'{{"details_open_accounts": {json_details_open_accounts}}}\n')
print(']')
  #datable = pd.DataFrame(details_open_accounts)
	###print(datable.info())
	##print(datable.describe())
	#print(datable.shape)
  #print(datable)

##building detalle_de_cuentas_cerradas_inactivas_table:
#if has_detalle_de_cuentas_cerradas_inactivas_table:
#  detalle_de_cuentas_cerradas_inactivas_table_index
#  detalle_de_cuentas_cerradas_inactivas_table_index_end = indagaciones_ultimos_6_meses_table_index - 1

#  #Get the slice of text about detalle_de_cuentas_cerradas_inactivas_table
#  detalle_de_cuentas_cerradas_inactivas_table_text = text[detalle_de_cuentas_cerradas_inactivas_table_index + 39 : detalle_de_cuentas_cerradas_inactivas_table_index_end]
#  #Making a list of each data split it of \n
#  details_of_open_close_accounts_list = detalle_de_cuentas_cerradas_inactivas_table_text.split('\n')
#  #print(details_of_open_close_accounts_list[13])

#  #Index where the each headers of de table ends
#  first_subscriber_row_start_index = details_of_open_close_accounts_list.index("<<---------") + 1 
#  last_subscriber_row_end_index = -1
#  #print(first_subscriber_row_start_index)
#  #print(last_subscriber_row_end_index)
#  details_of_close_accounts_list_data_rows = details_of_open_close_accounts_list[first_subscriber_row_start_index:]
#  #print(details_of_close_accounts_list_data_rows)


#####
  
#  # Processing the table rows for divide the information based in each suscriber data
#  details_of_close_accounts_list_suscribers_rows = []
#  sublista_actual = []  # Inicializar una sublista vacía

#  #Function processe data into details open account
#  #Split each suscriber data by ">>" character
#  # Separate the data in the suscriber element of account type and suscriber name
#  # Add each row modifyed to the final datatable
#  def process_table_details_closed_account(sublista_actual):
#    suscriptor = [sublista_actual[0]]
#    print(suscriptor)
#    #Separar la informacion del tipo de cuenta y el suscriptor por los caracteres ">>"
#    suscriptor = suscriptor[0].split(">>")

#    #Eliminar los espacios en blanco que tengan al principio y al fimal
#    for i in range (len (suscriptor)):
#      suscriptor[i] = suscriptor[i].strip()
#    # Crear las subsecuentes sublistas
#    sublistas_resto = [sublista_actual[i:i+11] for i in range(1, len(sublista_actual), 11)]

#    #Agregar el suscriptor a cada sublista (The data for each suscriber individualy)
#    sublista_con_suscriptor_agregado = []

#    for element in sublistas_resto:
#      element = suscriptor + element
#      sublista_con_suscriptor_agregado.append(element)

#    # Creating the final datatable with each row proccesed (suscriber and account type added)
#    for element in sublista_con_suscriptor_agregado:
#      details_of_close_accounts_list_suscribers_rows.append(element)
#  #End of function
    
#  ## Iterar a través de la lista original
#  for elemento in details_of_close_accounts_list_data_rows:

#    if ">>" in elemento:
#      # Si encontramos ">>", guardamos la sublista actual y creamos una nueva
#      if sublista_actual:
#        process_table_details_closed_account(sublista_actual)
#        sublista_actual = []

#    ### NO TOCAR PROXIMA LINEA
#    sublista_actual.append(elemento)  # Agregar elementos a la sublista actual

#  # Agregar la última sublista a la lista final
#  if sublista_actual:
#    process_table_details_closed_account(sublista_actual)
#    sublista_actual = [] 

#  #Turn the 12 month behavior vector in a list
#  #for element in details_of_close_accounts_list_suscribers_rows:
#  #  caracteres = element[12].replace(" ","")
#  #  lista_resultante = [int(caracter) if caracter.isdigit() else None for caracter in caracteres]

#  #  element[12] = lista_resultante
  
#  #>>>>>>>>>PRINT RESULT<<<<<<<<<<
#  #print(len(details_of_close_accounts_list_suscribers_rows))
#  #for row in details_of_close_accounts_list_suscribers_rows:
#  #  print(len(row))
#  #  print(row)

#  #details_close_accounts = [
#	#	{
#	#		"account_type": row[0],
#	#		"subscriber": row[1],
#	#		"status": row[2],
#	#		"update_date": row[3],
#	#		"opening_date": row[4],
#	#		"expiration_date": row[5],
#	#		"currency": row[6],
#	#		"credit_limit": row[7],
#	#		"current_balance": row[8],
#	#		"balance_in_arrears": row[9],
#	#		"minimum_payment_and_installment": row[10],
#	#		"no_of_installments_and_modality": row[11],
#	#		"behavior_vector_last_12_months": row[12],
#	#	}
#	#	for row in details_of_close_accounts_list_suscribers_rows
#	#]
#  #print(details_close_accounts)
#  #datable = pd.DataFrame(details_close_accountss)
#	###print(datable.info())
#	##print(datable.describe())
#	#print(datable.shape)
#  #print(datable)
