import csv
import smtplib
import datetime
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase


def show_summary(summary_name):
    totalbalance = 0
    debit = 0
    credit = 0
    string = ''
    months = {}
    with open(summary_name, 'r', newline='') as archivo_csv:
        reader = csv.DictReader(archivo_csv)
        for linea in reader:
            for campo, valor in linea.items():
                if(campo == "Transaction"):
                    string = f'{campo}:{valor}'
                    if(string[12] == "+"):
                        totalbalance += float(string[13:len(string)])
                        credit += float(string[13:len(string)])
                    if(string[12] == "-"):
                        totalbalance -= float(string[13:len(string)])
                        debit += float(string[13:len(string)])
                if(campo == "Date"):
                    string = f'{campo}:{valor}'
                    month = datetime.date(
                        2021, int(string[5]), 1).strftime('%B')
                    if month in months:
                        months[month] += 1
                    else:
                        months[month] = 1
    return {'Months': months, 'Total balance': totalbalance, 'Average Debit': debit, 'Average Credit': credit}


def send_msj(email, psw, destiny):
    try:
        mensaje = MIMEMultipart("alternative")
        mensaje["Subject"] = 'Account details'
        mensaje["From"] = email
        mensaje["To"] = destiny
        summary = show_summary('account.csv')
        totalmonth = ''
        for month, value in summary['Months'].items():
            totalmonth += '<li> Number of transactions in ' + \
                f'{month}:{value}'+'</li>'
        html = f"""
        <html>
            <div style="display:flex, flex-direction:column, align-content: center,">
                <img style="display: block; margin-left: auto; margin-right: auto;" src="data:image/png;base64,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
"><img>
                <h2 style="color:#384967;">Hi i hope you have a great day!</h2>
                <div style="background-color: #b3d3c8; border-radius: 10px; padding:20px;">
                    <h3 style="color=#fff">Account details:</h3>
                    <ul style="list-style-type: none;">
                        <li>Total balance is: ${summary['Total balance']}</li>
                    </ul>
                    <ul  style="list-style-type: none;">
                        <li>Average debit amount: ${summary['Average Debit']}</li>
                    </ul>
                    <ul  style="list-style-type: none;">
                        <li>Average credit amount: ${summary['Average Credit']}</li>
                    </ul>
                    <ul  style="list-style-type: none;">
                        {totalmonth}
                    </ul>
                </div>
            </div>
        <html>
        """
        archivo = "account.csv"
        with open(archivo, "rb") as adjunto:
            contenido_adjunto = MIMEBase("application", "octet-stream")
            contenido_adjunto.set_payload(adjunto.read())
        encoders.encode_base64(contenido_adjunto)
        contenido_adjunto.add_header(
            "Content-Disposition",
            f"attachment; filename={archivo}",
        )
        parte_html = MIMEText(html, "html")
        mensaje.attach(parte_html)
        mensaje.attach(contenido_adjunto)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, psw)
        server.sendmail(email, destiny, mensaje.as_string())
        server.quit()
    except(ValueError):
        print("Error email or password invalid")


def main():
    email = input("Log with your gmail email :")
    psw = getpass.getpass("Enter your password :")
    destiny = input("Enter recipient :")
    try:
        send_msj(email, psw, destiny)
    except(ValueError):
        print("Error email or password invalid")
    print("done")


if __name__ == '__main__':
    main()
