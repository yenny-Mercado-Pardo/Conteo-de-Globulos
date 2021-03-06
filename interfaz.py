from tkinter import Tk, Label, Button,Frame,LEFT,filedialog,BOTH,Entry,CENTER,Text,Scrollbar,END,Radiobutton,IntVar
from PIL import ImageTk, Image
from gb import ProcesamientoImagen
import cv2
import datetime
X_W = 1200
Y_H = 600
RESIZE_IMG = (int(X_W * 0.38-25), int(Y_H*0.95-25))
MEDIDA = "/mm3"
class Interfaz:
    def __init__(self, master):
        self.master = master
        #titulo de la ventana
        self.master.title("Conteo de globulos")

        #dimensionando la ventana principal
        self.master.geometry(str(X_W)+ "x" + str(Y_H))

        #creando panel de control
        self.panelControl = Frame(master,width=X_W * 0.24,height=Y_H)
        self.panelControl.pack_propagate(0)
        self.panelControl.pack(side=LEFT)
        self.panelControl.configure(background='pink')

        #creando visualizacion de imagen inicial
        self.visualizacion = Frame(master,width=X_W * 0.38,height=Y_H)
        self.visualizacion.pack_propagate(0)
        self.visualizacion.pack(side=LEFT)
        self.visualizacion.config(cursor="pirate")
        self.visualizacion.config(bd=10)
        self.visualizacion.config(relief="sunken")
        self.visualizacion.config(background="pink")
        #poniendole un titulo
        self.titulo = Label(self.visualizacion, text="Imagen original")
        self.titulo.pack()

        # creando visualizacion de imagen procesada
        self.procesado = Frame(master, width=X_W * 0.38, height=Y_H)
        self.procesado.pack_propagate(0)
        self.procesado.pack(side=LEFT)
        self.procesado.config(cursor="pirate")
        self.procesado.config(bd=10)
        self.procesado.config(relief="sunken")
        self.procesado.config(background="pink")
        #poniendo un titulo
        self.tituloProcesado = Label(self.procesado, text="Imagen Procesada")
        self.tituloProcesado.pack()

        # creando el label para imagen original
        self.panel = Label(self.visualizacion)
        self.panel.place(x=0, y=int(Y_H - Y_H * 0.95))
        self.pathOriginal = None;

        # creando el label para imagen procesada
        self.panelProcesado = Label(self.procesado)
        self.panelProcesado.place(x=0, y=int(Y_H - Y_H * 0.95))

        # definiendo los controles
        #titulo
        self.tituloControl = Label(self.panelControl, text="Controles",height=2).pack(fill=BOTH)

        self.fontBtn = ('Sans','10','bold')
        #open file
        self.loadFile = Button(self.panelControl,  command=self.open_img, height=2,
            relief = "groove", compound = CENTER, text="Cargar imagen",font = self.fontBtn ).pack(fill=BOTH,padx=10, pady=10)

        #frame para conectarse a la camara ip
        self.frameCamera = Frame(self.panelControl)
        self.frameCamera.pack_propagate(0)
        self.frameCamera.pack(fill=BOTH,padx=10)

        #input link de la camara ip
        self.entryLink = Entry(self.frameCamera)
        self.entryLink.grid(row=0,column=0)
        self.entryLink.insert(0,'http://192.168.0.3:8080/video')

        #button de conexion
        self.connectButton = Button(self.frameCamera,text="C",command=self.prepareIpCamera)
        self.connectButton.grid(row=0,column=1)

        #button de captura de imagen
        self.snaptshotButton = Button(self.frameCamera, text="S",command=self.snapShotCamera)
        self.snaptshotButton.grid(row=0, column=2)

        # para el video
        self.stopCamera = Button(self.frameCamera, text="[]", command=self.stopStreamVideo)
        self.stopCamera.grid(row=0, column=3)


        #aplicando el analisis
        self.applyProceso = Button(self.panelControl, command=self.procesarOpencv, height=2,
                           relief="groove", compound=CENTER, text="Procesar",font = self.fontBtn).pack(fill=BOTH, padx=10,pady=10)

        # aplicando el analisis
        #self.applyStepProceso = Button(self.panelControl, command=self.callStepProcess, height=2,
        #                relief="groove", compound=CENTER, text="Paso por paso").pack(fill=BOTH, padx=10)

        self.clearProcess = Button(self.panelControl, command=self.limpiarVisualizador, height=2,
                        relief="groove", compound=CENTER, text="Limpiar",font = self.fontBtn).pack(fill=BOTH, padx=10)

        self.valor = IntVar()
        self.valor.set(1)
        self.radioButton1 = Radiobutton(self.panelControl, text="total(blanco) = XXX * 20 * 2.5 "+MEDIDA, variable=self.valor, value=1)
        self.radioButton1.pack(fill=BOTH, padx=10)
        self.radioButton2 = Radiobutton(self.panelControl, text="total(rojo) = XXX * 200 * 10 * 5 "+MEDIDA, variable=self.valor, value=2)
        self.radioButton2.pack(fill=BOTH, padx=10)

        #scroll a modo de consola
        self.textArea = Text(self.panelControl)
        self.textArea.pack(fill=BOTH, padx=10,pady=10, expand=1)
        scroll_y = Scrollbar(self.textArea, orient="vertical", command=self.textArea.yview)
        scroll_y.pack(side="right", fill="y")
        self.textArea.configure(yscrollcommand=scroll_y.set)

        self.captureStrem = False
        self.streamVideo = None

    def calcularRojos(self,cantidad):
        self.printLn("C. eritrocitos " + str(cantidad * 200 * 10 * 5 ) + MEDIDA)

    def calcularBlancos(self, cantidad):
        self.printLn("C. leucocitos " + str(cantidad * 20 * 2.5) + MEDIDA)

    def stopStreamVideo(self):
        self.captureStrem = False
        self.streamVideo = None
        self.clearOriginal()

    def prepareIpCamera(self):
        self.connectCamera()
        self.videoStreamIpCamera()

    def connectCamera(self):
        link = self.entryLink.get()
        try:
            self.printLn("Connect: " + link )
            self.streamVideo = cv2.VideoCapture(link)
            self.clearProcesado()
        except:
            self.printLn("Verifique la direccion, no se ha podido conectar")

    def snapShotCamera(self):
        if self.streamVideo is None:
            return
        if self.streamVideo.isOpened():
            ret,frame = self.streamVideo.read()
            #cortando la transmision
            self.streamVideo = None
            # guardando la imagen
            directorio = "camera/" + str(datetime.datetime.now()) + ".jpg"
            cv2.imwrite(directorio, frame)
            #cv2image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            img = img.resize(RESIZE_IMG, Image.BICUBIC)
            #mostrando el resultado en pantalla
            self.showFrameImage(img)
            self.pathOriginal = directorio

    def videoStreamIpCamera(self):
        if self.streamVideo is None:
            return
        if self.streamVideo.isOpened():
            ret, frame = self.streamVideo.read()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            img = img.resize(RESIZE_IMG, Image.BICUBIC)
            self.showFrameImage(img)
            self.panel.after(1,self.videoStreamIpCamera)
        else:
            self.printLn("Verifique su conexion")
            return

    def printLn(self, text):
        self.textArea.insert(END, str(text) + "\n")

    def callStepProcess(self):
        if self.pathOriginal is None:
            self.printLn("Sebe seleccionar la imagen")
            return
        process = ProcesamientoImagen(self.pathOriginal)
        process.showAllStep()

    def showCantidad(self,cantidad):
        if( self.valor.get() == 2):
            self.calcularRojos(cantidad)
        else:
            self.calcularBlancos(cantidad)

    def limpiarVisualizador(self):
        self.clearOriginal()
        self.clearProcesado()
        self.pathOriginal= None

    def clearOriginal(self):
        self.panel.config(image=None)
        self.panel.image = None

    def clearProcesado(self):
        self.panelProcesado.config(image=None)
        self.panelProcesado.image = None

    def procesarOpencv(self):
        if self.pathOriginal is None:
            self.printLn("Debe seleccionar una imagen")
            return
        procesarImg = ProcesamientoImagen(self.pathOriginal)
        array,region = procesarImg.procesar()
        img = Image.fromarray(array)
        img = img.resize(RESIZE_IMG, Image.BICUBIC)
        self.showFrameProcesado(img)
        self.printLn("Total: " + str(len(region)))
        self.showCantidad(len(region))

    def showFrameProcesado(self,img):
        frame = ImageTk.PhotoImage(img)
        self.panelProcesado.config(image=frame)
        self.panelProcesado.image = frame

    def showFrameImage(self,img):
        frame = ImageTk.PhotoImage(img)
        self.panel.config(image=frame)
        self.panel.image = frame

    def open_img(self):
        x = self.openfn()
        if( not x): return
        self.pathOriginal = x
        self.printLn(x)
        img = Image.open(x)
        img = img.resize(RESIZE_IMG, Image.BICUBIC)
        self.showFrameImage(img)
        self.clearProcesado()

    def openfn(self):
        filename = filedialog.askopenfilename(title='open')
        return filename

root = Tk()
root.resizable(False, False)
windows = Interfaz(root)
root.mainloop()