from tkinter import Tk, Label, Button,Frame,LEFT,filedialog,BOTH,TOP,RAISED,CENTER,Text,Scrollbar,END
from PIL import ImageTk, Image
from gb import ProcesamientoImagen
X_W = 1200
Y_H = 600
RESIZE_IMG = (int(X_W * 0.38-25), int(Y_H*0.95-25))

class Interfaz:
    def __init__(self, master):
        self.master = master
        #titulo de la ventana
        self.master.title("Taller de redes")

        #dimensionando la ventana principal
        self.master.geometry(str(X_W)+ "x" + str(Y_H))

        #creando panel de control
        self.panelControl = Frame(master,width=X_W * 0.24,height=Y_H)
        self.panelControl.pack_propagate(0)
        self.panelControl.pack(side=LEFT)

        #creando visualizacion de imagen inicial
        self.visualizacion = Frame(master,width=X_W * 0.38,height=Y_H)
        self.visualizacion.pack_propagate(0)
        self.visualizacion.pack(side=LEFT)
        self.visualizacion.config(cursor="pirate")
        self.visualizacion.config(bd=10)
        self.visualizacion.config(relief="sunken")
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
        #open file
        self.loadFile = Button(self.panelControl,  command=self.open_img, height=2,
            relief = "groove", compound = CENTER, text="Cargar imagen").pack(fill=BOTH,padx=10, pady=10)

        #aplicando el analisis
        self.applyProceso = Button(self.panelControl, command=self.procesarOpencv, height=2,
                           relief="groove", compound=CENTER, text="Procesar").pack(fill=BOTH, padx=10)

        self.formulaGB = Label(self.panelControl, text="total = XXX * 20 * 2.5 (mxx)").pack(fill=BOTH,padx=10)
        self.formulaGR = Label(self.panelControl, text="total = XXX * 200 * 10 * 5 (mxx)").pack(fill=BOTH,padx=10)

        #scroll a modo de consola
        self.textArea = Text(self.panelControl)
        self.textArea.pack(fill=BOTH, padx=10,pady=10, expand=1)
        scroll_y = Scrollbar(self.textArea, orient="vertical", command=self.textArea.yview)
        scroll_y.pack(side="right", fill="y")
        self.textArea.configure(yscrollcommand=scroll_y.set)

    def printLn(self, text):
        self.textArea.insert(END, str(text) + "\n")

    def procesarOpencv(self):
        procesarImg = ProcesamientoImagen(self.pathOriginal)
        array,region = procesarImg.procesar()
        img = Image.fromarray(array)
        img = img.resize(RESIZE_IMG, Image.BICUBIC)
        img = ImageTk.PhotoImage(img)
        self.panelProcesado.config(image=img)
        self.panelProcesado.image = img
        self.printLn("cantidad: " + str(len(region)))

    def open_img(self):
        x = self.openfn()
        if( not x): return
        self.pathOriginal = x
        self.printLn(x)
        img = Image.open(x)
        img = img.resize(RESIZE_IMG, Image.BICUBIC)
        img = ImageTk.PhotoImage(img)
        self.panel.config(image=img)
        self.panel.image = img

    def openfn(self):
        filename = filedialog.askopenfilename(title='open')
        return filename

root = Tk()
root.resizable(False, False)
windows = Interfaz(root)
root.mainloop()


# => GR
# => total = XXX * 200 * 10 * 5 (mxx)

# => GB
# => total = XXX * 20 * 2.5 (mxx)