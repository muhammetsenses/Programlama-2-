import csv
import os

import mysql.connector
import pandas as pd
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QGroupBox, QLineEdit, \
    QPushButton
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression


def DolarParse():
    # Dolar verileri çekilecek site:
    URL = "https://www.doviz724.com/2020-agustos-ayinda-amerikan-dolari-fiyati-ne-kadardi.html"
    # Siteyi python ile açıyoruz / siteyi getiriyoruz
    r = requests.get(URL)
    # sitede(ki/nin) verileri/içeriğini/kodlarını "BeautifulSoup" ile çekiyoruz
    soup = BeautifulSoup(r.content, "html.parser")
    # sitedeki belirli bir "table" elementine ulaşıyoruz (class'ı aşağıdaki gibi belirli olan)
    getData = soup.find("table", {"class": "table table-striped"})
    # "table" elementi içindeki "span" elementlerini buluyoruz
    childs = getData.find_all("span")
    # span elementi içinde tarih/alış/satış bilgileri var
    # ama bize sadece satış gerekli bu yüzden sadece satış-
    # verilerini tutacak olan "dolars" adlı bir liste oluşturuyoruz
    dolars = []

    # bir gün sonraki doları tahmin etmede bize tarihlerde gerekli
    dates = []

    # span içindeki tüm elemanları geziyoruz
    for i in range(len(childs)):
        # sadece satış bilgilerini alacağız
        # satış bilgileri ise listede 2, 5, 8 indexlerinde bulunmakta
        # yani 3. elemandan başlayarak üçer üçer bulunmakta
        # bunuda 3'e mod alarak hesaplıyoruz
        # 2, 5, 8'in 3'a kalanı 2'dir
        if i % 3 == 2:
            # liseteye satış bilgisini ekliyoruz
            # text diyerek sadece element içindeki yazıyı getiriyoruz
            # ama yazının sonunda " TL" ibaresi bulunmakta
            # bunu ise string'in son 3 elemanını dahil etmeyerek çıkartıyoruz
            dolars.append(childs[i].text[:-3])

        # aynı şekilde tarih bilgilerinide çekiyoruz
        if i % 3 == 0:
            dates.append(childs[i].text.split("-")[0])

    # çekilen veriler pandas ile csv dosyasına yazdırılıyor
    my_df = pd.DataFrame({"gün": dates, "dolar": dolars})
    my_df.to_csv('dolar.csv', index=False, header=False)


# class pencere özelliklerini QWidget'tan miras almakta
# böylelikle basit bir pencere gösterebileceğiz
class Window(QWidget):

    # initialize fonksiyonunu override ediyoruz
    # yani class oluşturulduğunda çalışacak fonksiyonları yazıyoruz
    def __init__(self):
        # super fonksiyonunu çağırıyoruzki QWidget'a ait özellikleri kullanabilelim
        # çağırmadığımız taktirde zaten hata alıyoruz,bu hatayı gidermek içinde çağırmak zorundayız
        super().__init__()

        # pencerenin başlığını ayarlıyoruz
        self.setWindowTitle("DOLAR KAR/ZARAR HESAPLAMA")

        # pencereye ekleyeceğimiz elemanları hangi düzene ekleyecek isek o düzeni oluşturuyoruz
        # Burada Vertical/dikey bir şekilde eleman ekleyeceğimizi belirttik
        # değişkeni self şeklinde oluşturmamızın sebebi bunun class'a ait bir değişken olduğunu belirtmek
        self._layout = QVBoxLayout()

        # oluşturacağımız "group" kısmı içinde düzen oluşturmamız gerekli
        self._groupLayout = QVBoxLayout()
        self._groupLayout2 = QVBoxLayout()
        self._groupLayout3 = QVBoxLayout()

        # ürün ekle kısmı yatay olacağından dolayı birde hortizonal/yatay düzen ekliyoruz
        self._hLayout = QHBoxLayout()

        # pencerenin minimum boyutlarını ayarlıyoruz
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        # fonksiyonu çağırarak son 1 ayki dolar kuru liste şeklinde tanımlanıyor
        self.dolars = []

        # tahmin için tarih listesini değişkene atıyoruz
        self.dates = []

        # eğer daha önce dolar-gün bilgilerine ait dosya oluşturulmamışsa oluşturuluyor
        if not os.path.isfile('./dolar.csv'):
            DolarParse()

        # gün-dolar bilgilerini içeren dosya okunuyor
        with open("dolar.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                # dolar ve gün oluşturulan listelere atanıyor
                self.dolars.append(row[1])
                self.dates.append(int(row[0]))

        # dolar yazısını yazdıracağımız widget'ı/elemanı oluşturuyoruz
        # metni ise çektiğimiz listenin son elemanına ayarlıyoruz
        # buda güncel dolar kuruna denk gelmekte
        # ama bunu direkt olarak yazdıramayız string türüne çevirmemiz gerekli
        # stringlerde birleştirme işlemi toplama opareterü ile yapılabilmekte
        self.dolarText = QLabel(" Güncel dolar kuru: " + self.dolars[-1])
        # basit CSS kodları ile yazının yazı fontu ve büyüklüğü ayarlandı:
        # CSS: internet sitelerinin dizaynında kullanılan kodlama türü
        self.dolarText.setStyleSheet("font: 18px Courier New;")

        # ürünlerinin listesini tutacağımız açılır/kapanır listemiz için widget'ımızı belirledik
        self.products = QComboBox()

        # Ürünler ile alakalı kısmı bir grup içinde topluyoruz (görüntüsel olarak)
        self.group = QGroupBox("Ürünler")

        # ürün ekle kısmı için bir yazı alanı ve "ekle" butonu oluşturuyoruz
        self.addproductBar = QLineEdit()
        self.addproductBtn = QPushButton("EKLE")

        self.addproductBtn.clicked.connect(self.addItem)
        # ipucu için önizleme metni ayarlanıyor:
        self.addproductBar.setPlaceholderText("Eklenecek ürünün ismini girin")

        # kar/zarar işlemlerini yapacağımız kısmı bir grupta topluyoruz (görüntüsel olarak)
        self.group2 = QGroupBox("Kar/Zarar İşlemleri")

        # alış ve satış fiyatları için metin kutuları oluşturuluyor
        self.purchasePrice = QLineEdit()
        self.purchasePrice.setPlaceholderText(
            "Alış fiyatı | dolar üzerinden (orn: 250$) | dolar işareti '$' konulmamalıdır!")
        self.salePrice = QLineEdit()
        self.salePrice.setPlaceholderText("Satış fiyatı | TL üzerinden (orn: 250₺) | TL işareti '₺' konulmamalıdır!")
        self.calcButton = QPushButton("HESAPLA")

        self.calcButton.clicked.connect(self.caclProfit)

        self.urunler_alis_satis = []

        # database'deki ürünleri listeye/combobox'a ekliyoruz
        # gerekli alanları güncelliyoruz
        mycursor.execute("SELECT * FROM urunler")
        myresult = mycursor.fetchall()
        self.index = 0  # ürünlerin toplam index'ini tutuyoruz
        for item in myresult:
            self.index += 1
            self.products.addItem(item[1])
            self.urunler_alis_satis.append([item[2], item[3]])

        # başlangıçtada liste güncelleniyor
        self.updateList()

        # combobox'ı güncellemek adına seçimdeki değişimi algılayıp bir fonksiyona bağlıyoruz
        self.products.currentIndexChanged.connect(self.updateList)

        # sonuçları bir grupta topluyoruz (görüntüsel olarak)
        self.group3 = QGroupBox("Sonuçlar")
        # kâr/zarar tutacak widget'ı oluşturuyoruz
        self.profitAndLoss = QLabel("Bugünki kâr/Zarar: ")
        self.gProfitAndLoss = QLabel("Yarın ki tahmini kâr/Zarar: ")

        # oluşturduğumuz düzenin içine elemanlarımızı ekliyoruz
        self._layout.addWidget(self.dolarText)

        self._layout.addWidget(self.group2)
        self.group2.setLayout(self._groupLayout2)
        self._groupLayout2.addWidget(self.purchasePrice)
        self._groupLayout2.addWidget(self.salePrice)
        self._groupLayout2.addWidget(self.calcButton)
        self._layout.addWidget(self.group3)
        self.group3.setLayout(self._groupLayout3)
        self._groupLayout3.addWidget(self.profitAndLoss)
        self._groupLayout3.addWidget(self.gProfitAndLoss)

        # Sonradan alta taşındığı için değişken isimleri sırası ile değil
        self._layout.addWidget(self.group)
        self.group.setLayout(self._groupLayout)
        self._groupLayout.addWidget(self.products)
        self._groupLayout.addLayout(self._hLayout)
        self._hLayout.addWidget(self.addproductBar)
        self._hLayout.addWidget(self.addproductBtn)

        # görüntü açısında widgetların altına uzatma ekliyoruz
        self._layout.addStretch()

        # class'ın yani QWidget'ın kullanacağı düzen sistemini ayarlıyoruz
        self.setLayout(self._layout)

        # pencereyi biz göstermediğimiz taktirde görünmeyecektir
        self.show()

    def caclProfit(self):
        # virgün ile hesaplama yapılamayacağı için virgül noktaya çeviriliyor
        floatDolar = float(self.dolars[-1].replace(",", "."))

        profitAndLoss = float(self.salePrice.text()) - (float(self.purchasePrice.text()) * floatDolar)
        self.profitAndLoss.setText("Bugünki kâr/Zarar: " + str(profitAndLoss))

        # tahmini dolar bilgisi çekiliyor
        floatPredictedDolar = self.prediction()
        # tahmini kar/zarar hesaplamaları yapılıyor
        # :.4f ise ondalık kısmın 4 basamağının yazdıralacağını ifade etmekte
        predictProfitAndLoss = float(self.salePrice.text()) - (float(self.purchasePrice.text()) * floatPredictedDolar)
        self.gProfitAndLoss.setText(
            "Yarın ki tahmini kâr/Zarar: {} (tahmini dolar: {:.4f})".format(predictProfitAndLoss, floatPredictedDolar))

    def addItem(self):
        self.index += 1
        # database'e eklemek için gerekli sql kodu yazılıyor
        sqlFormula = "INSERT INTO urunler (urunlerid, urunler_isim, urunler_alis, urunler_satis) VALUES (%s, %s, %s, %s)"
        # ürün eklenmek için mevcut index ve yazısı ile tuple olarak değişkene atılıyor
        urun = (self.index, self.addproductBar.text(), self.purchasePrice.text(), self.salePrice.text())
        # ürün database'e yazdırılıyor
        mycursor.execute(sqlFormula, urun)

        # eklenen ürünün alış satış fiyatları listeye eklenioyor
        self.urunler_alis_satis.append([self.purchasePrice.text(), self.salePrice.text()])

        # aynı şekilde görüntüsel olarakta güncellemeler yapılıyor
        self.products.addItem(self.addproductBar.text())
        self.products.setCurrentIndex(self.index - 1)
        self.addproductBar.setText("")

        # database'e işleniyor
        cnx.commit()

    def prediction(self):
        # gün ve dolar bilgileri gerekli formata çeviriliyor
        x = [[x] for x in self.dates]
        y = [[float(x.replace(",", "."))] for x in self.dolars]

        # Doğrusal regresyon sınıfı çağırılıyor
        model = LinearRegression()
        model.fit(x, y)

        # yarınki tahmin yapılıyor
        y_pred_sklearn = model.predict([[self.dates[-1] + 1]])
        return float(y_pred_sklearn[0][0])

    def updateList(self):
        # liste boş değilse güncelleniyor
        if self.products.currentIndex() != -1:
            self.purchasePrice.setText(str(self.urunler_alis_satis[self.products.currentIndex()][0]))
            self.salePrice.setText(str(self.urunler_alis_satis[self.products.currentIndex()][1]))


# pencere oluşturmak için temel kodlar yazıldı:
app = QApplication([])  # içine boş liste koymazsak hata alıyoruz

# database'e bağlanıyoruz
cnx = mysql.connector.connect(user='root', password='1234', host='localhost')
# işaretciyi/imleci oluşturuyoruz
mycursor = cnx.cursor()
# eğer database daha önce oluşturulmamış ise oluşturuyoruz
mycursor.execute("CREATE DATABASE IF NOT EXISTS odev")
# oluşturduğumuz veya var olan database'e bağlanıyoruz
cnx = mysql.connector.connect(user='root', password='1234', host='localhost', database='odev')
mycursor = cnx.cursor()
# Eğer database'de urunler tablosu yoksa oluşturuyoruz
mycursor.execute(
    "CREATE TABLE IF NOT EXISTS urunler (urunlerid INT AUTO_INCREMENT PRIMARY KEY, urunler_isim VARCHAR(40), urunler_alis INT, urunler_satis INT);")

window = Window()  # pencere oluşturacağımız class çağrılıyor
app.exec_()
