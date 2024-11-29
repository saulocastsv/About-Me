import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from yt_dlp import YoutubeDL
import threading
import os

class YouTubeDownloaderApp:
    def __init__(self, root):
        
        self.root = root
        self.root.title("Baixar Vídeo do Youtube")
        self.root.geometry("720x560")
        self.root.resizable(False, False)

        # Armazena os links e opções
        self.links_and_options = []
        self.output_directory = tk.StringVar(value=os.getcwd())  # Pasta padrão: atual

        # Layout
        self.create_widgets()

    def create_widgets(self):
        # Título
        ttk.Label(self.root, text="Baixador de vídeos IC", font=("Poppins", 16)).pack(pady=10)

        # Entrada de links
        self.num_links = tk.IntVar(value=1)
        ttk.Label(self.root, text="Quantos links deseja baixar? Máximo de 5").pack()
        ttk.Spinbox(self.root, from_=1, to=5, textvariable=self.num_links, width=5).pack(pady=5)

        # Botão para confirmar número de links
        ttk.Button(self.root, text="Confirmar", command=self.show_link_fields).pack(pady=10)

        # Escolha de diretório de saída
        ttk.Label(self.root, text="Pasta para salvar os downloads:").pack(pady=5)
        output_frame = ttk.Frame(self.root)
        output_frame.pack(pady=5)
        ttk.Entry(output_frame, textvariable=self.output_directory, width=40).pack(side="left", padx=5)
        ttk.Button(output_frame, text="Escolher pasta onde salvar", command=self.choose_directory).pack(side="left")

        # Área para campos de link
        self.links_frame = ttk.Frame(self.root)
        self.links_frame.pack(pady=10)

        # Spinner de carregamento
        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(pady=5)
        self.progress.pack_forget()  # Esconde inicialmente

        # Rodapé para status
        self.status_label = ttk.Label(self.root, text="Status: Aguardando ação...", relief="sunken", anchor="w")
        self.status_label.pack(side="bottom", fill="x", padx=5, pady=5)

    def choose_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_directory.set(directory)

    def show_link_fields(self):
        # Limpar links anteriores
        for widget in self.links_frame.winfo_children():
            widget.destroy()

        # Gerar campos para links e opções
        self.links_and_options = []
        for i in range(self.num_links.get()):
            frame = ttk.Frame(self.links_frame)
            frame.pack(fill="x", pady=5)

            ttk.Label(frame, text=f"Link {i + 1}:").pack(side="left", padx=5)
            link_var = tk.StringVar()
            ttk.Entry(frame, textvariable=link_var, width=40).pack(side="left", padx=5)

            convert_var = tk.BooleanVar()
            ttk.Checkbutton(frame, text="Converter para MP3", variable=convert_var).pack(side="left", padx=5)

            self.links_and_options.append({"link_var": link_var, "convert_var": convert_var})

        # Botão para iniciar o download
        ttk.Button(self.root, text="Iniciar Download", command=self.start_download_thread).pack(pady=10)

    def start_download_thread(self):
        # Inicia o download em uma thread separada para evitar congelar a interface
        thread = threading.Thread(target=self.start_download)
        thread.start()

    def start_download(self):
        # Coletar links e opções
        links_and_options = []
        for item in self.links_and_options:
            url = item["link_var"].get().strip()
            convert_to_mp3 = item["convert_var"].get()
            if url:
                links_and_options.append({"url": url, "convert_to_mp3": convert_to_mp3})

        if not links_and_options:
            messagebox.showerror("Erro", "Você deve fornecer pelo menos um link válido.")
            return

        # Mostrar spinner e atualizar status
        self.progress.pack()  # Exibe o spinner
        self.progress.start(10)  # Inicia o spinner
        self.status_label.config(text="Status: Iniciando downloads...")

        # Processar cada link
        for index, item in enumerate(links_and_options, start=1):
            url = item['url']
            convert_to_mp3 = item['convert_to_mp3']
            self.status_label.config(text=f"Baixando vídeo {index}/{len(links_and_options)}...")

            # Configurações de download
            video_options = {
                'format': 'best',
                'outtmpl': os.path.join(self.output_directory.get(), f'video_{index}_%(title)s.%(ext)s'),
            }

            # Adicionar conversão para MP3, se necessário
            if convert_to_mp3:
                video_options.update({
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
                })

            try:
                with YoutubeDL(video_options) as ydl:
                    ydl.download([url])
            except Exception as e:
                self.progress.stop()
                self.progress.pack_forget()
                messagebox.showerror("Erro", f"Erro ao processar o vídeo {index}: {e}")
                self.status_label.config(text="Status: Erro durante o download.")
                return

        # Concluir processo
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.config(text="Status: Todos os downloads concluídos!")
        messagebox.showinfo("Concluído", "Todos os downloads foram concluídos com sucesso!")

# Executar a aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
