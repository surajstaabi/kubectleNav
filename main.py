# Made by mochiron-desu
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import queue
import sys

# Helper to run kubectl commands
def run_kubectl_cmd(args):
    try:
        result = subprocess.run([
            'kubectl', *args
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        return []

class LogViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Kubectl Pod/Container Logs Viewer')
        self.namespace = 'default'
        self.log_thread = None
        self.stop_event = threading.Event()
        self.log_queue = queue.Queue()

        # UI
        self.ns_label = ttk.Label(root, text='Namespace:')
        self.ns_label.grid(row=0, column=0, sticky='w')
        self.ns_combo = ttk.Combobox(root, state='readonly')
        self.ns_combo.grid(row=0, column=1, sticky='ew')
        self.ns_combo.bind('<<ComboboxSelected>>', self.on_namespace_selected)

        self.pod_label = ttk.Label(root, text='Pod:')
        self.pod_label.grid(row=0, column=2, sticky='w')
        self.pod_combo = ttk.Combobox(root, state='readonly')
        self.pod_combo.grid(row=0, column=3, sticky='ew')
        self.pod_combo.bind('<<ComboboxSelected>>', self.on_pod_selected)

        self.container_label = ttk.Label(root, text='Container:')
        self.container_label.grid(row=0, column=4, sticky='w')
        self.container_combo = ttk.Combobox(root, state='readonly')
        self.container_combo.grid(row=0, column=5, sticky='ew')

        self.tail_label = ttk.Label(root, text='Show last N lines:')
        self.tail_label.grid(row=0, column=6, sticky='w')
        self.tail_var = tk.StringVar(value='1000')
        self.tail_entry = ttk.Entry(root, textvariable=self.tail_var, width=6)
        self.tail_entry.grid(row=0, column=7, sticky='ew')

        self.live_var = tk.BooleanVar(value=True)
        self.live_check = ttk.Checkbutton(root, text='Live (follow new logs)', variable=self.live_var)
        self.live_check.grid(row=0, column=8, sticky='w')

        self.show_btn = ttk.Button(root, text='Show Logs', command=self.show_logs)
        self.show_btn.grid(row=0, column=9, padx=5)
        self.stop_btn = ttk.Button(root, text='Stop Logs', command=self.stop_logs, state='disabled')
        self.stop_btn.grid(row=0, column=10, padx=5)

        self.clear_btn = ttk.Button(root, text='Clear Logs', command=self.clear_logs)
        self.clear_btn.grid(row=0, column=11, padx=5)

        self.log_text = scrolledtext.ScrolledText(root, wrap='word', height=30, width=100, state='disabled')
        self.log_text.grid(row=1, column=0, columnspan=12, sticky='nsew', pady=5)

        self.status_var = tk.StringVar()
        self.status_var.set('Ready')
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief='sunken', anchor='w')
        self.status_bar.grid(row=2, column=0, columnspan=11, sticky='ew')
        self.signature_label = ttk.Label(root, text='Made by mochiron-desu', relief='sunken', anchor='e', font=('TkDefaultFont', 8, 'italic'))
        self.signature_label.grid(row=2, column=11, sticky='ew')

        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(3, weight=1)
        root.grid_columnconfigure(5, weight=1)
        root.grid_rowconfigure(1, weight=1)

        self.populate_namespaces()
        self.update_log_text()

    def set_loading(self, loading=True, message='Loading...'):
        controls = [self.ns_combo, self.pod_combo, self.container_combo, self.show_btn, self.stop_btn, self.clear_btn]
        state = 'disabled' if loading else 'readonly'
        for ctrl in controls:
            if isinstance(ctrl, ttk.Combobox):
                ctrl['state'] = state
            else:
                ctrl['state'] = 'disabled' if loading else 'normal'
        self.status_var.set(message)

    def populate_namespaces(self):
        self.set_loading(True, 'Loading namespaces...')
        self.root.after(100, self._populate_namespaces)

    def _populate_namespaces(self):
        namespaces = run_kubectl_cmd(['get', 'namespaces', '-o', 'jsonpath={.items[*].metadata.name}'])
        ns_list = namespaces[0].split() if namespaces else ['default']
        self.ns_combo['values'] = ns_list
        if self.namespace in ns_list:
            self.ns_combo.set(self.namespace)
        else:
            self.ns_combo.current(0)
            self.namespace = self.ns_combo.get()
        self.set_loading(False, 'Namespaces loaded.')
        self.on_namespace_selected()

    def on_namespace_selected(self, event=None):
        self.namespace = self.ns_combo.get()
        self.set_loading(True, f'Loading pods in namespace {self.namespace}...')
        self.root.after(100, self._populate_pods)

    def populate_pods(self):
        self.set_loading(True, f'Loading pods in namespace {self.namespace}...')
        self.root.after(100, self._populate_pods)

    def _populate_pods(self):
        pods = run_kubectl_cmd(['get', 'pods', '-n', self.namespace, '-o', 'jsonpath={.items[*].metadata.name}'])
        pod_list = pods[0].split() if pods else []
        self.pod_combo['values'] = pod_list
        if pod_list:
            self.pod_combo.current(0)
            self.set_loading(False, 'Pods loaded.')
            self.on_pod_selected()
        else:
            self.pod_combo.set('')
            self.container_combo.set('')
            self.container_combo['values'] = []
            self.set_loading(False, 'No pods found.')

    def on_pod_selected(self, event=None):
        pod = self.pod_combo.get()
        if not pod:
            self.container_combo['values'] = []
            self.container_combo.set('')
            self.status_var.set('No pod selected.')
            return
        self.set_loading(True, f'Loading containers in pod {pod}...')
        self.root.after(100, lambda: self._populate_containers(pod))

    def _populate_containers(self, pod):
        containers = run_kubectl_cmd([
            'get', 'pod', pod, '-n', self.namespace, '-o', 'jsonpath={.spec.containers[*].name}'
        ])
        container_list = containers[0].split() if containers else []
        self.container_combo['values'] = container_list
        if container_list:
            self.container_combo.current(0)
            self.set_loading(False, 'Containers loaded.')
        else:
            self.container_combo.set('')
            self.set_loading(False, 'No containers found.')

    def show_logs(self):
        pod = self.pod_combo.get()
        container = self.container_combo.get()
        tail = self.tail_var.get()
        live = self.live_var.get()
        if not pod:
            messagebox.showerror('Error', 'Please select a pod.')
            return
        try:
            tail_n = int(tail)
            if tail_n < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror('Error', 'Please enter a valid positive integer for N.')
            return
        self.stop_event.clear()
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state='disabled')
        self.show_btn['state'] = 'disabled'
        self.stop_btn['state'] = 'normal'
        self.status_var.set('Loading logs...')
        self.log_thread = threading.Thread(target=self.stream_logs, args=(pod, container, tail_n, live), daemon=True)
        self.log_thread.start()

    def stream_logs(self, pod, container, tail_n, live):
        cmd = ['kubectl', 'logs', pod, '-n', self.namespace, f'--tail={tail_n}']
        if container:
            cmd += ['-c', container]
        if live:
            cmd += ['-f']
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if process.stdout is not None:
                for line in process.stdout:
                    if self.stop_event.is_set():
                        process.terminate()
                        break
                    self.log_queue.put(line)
                process.stdout.close()
                process.wait()
            else:
                self.log_queue.put('Error: Failed to capture process stdout.\n')
        except Exception as e:
            self.log_queue.put(f'Error: {e}\n')
        self.show_btn['state'] = 'normal'
        self.stop_btn['state'] = 'disabled'

    def stop_logs(self):
        self.stop_event.set()
        self.show_btn['state'] = 'normal'
        self.stop_btn['state'] = 'disabled'
        self.status_var.set('Log streaming stopped.')

    def update_log_text(self):
        try:
            got_line = False
            while True:
                line = self.log_queue.get_nowait()
                got_line = True
                self.log_text.configure(state='normal')
                # Check if user is at the bottom before inserting
                last_visible = self.log_text.yview()[1]
                self.log_text.insert(tk.END, line)
                if last_visible >= 0.999:  # Only auto-scroll if at bottom
                    self.log_text.see(tk.END)
                self.log_text.configure(state='disabled')
            if got_line:
                self.status_var.set('Streaming logs...')
        except queue.Empty:
            pass
        self.root.after(100, self.update_log_text)

    def clear_logs(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state='disabled')
        self.status_var.set('Logs cleared.')

    def on_close(self):
        # Set stop event to stop log streaming
        self.stop_event.set()
        # Wait for log thread to finish if it's running
        if self.log_thread and self.log_thread.is_alive():
            self.log_thread.join(timeout=2)
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = LogViewerApp(root)
    root.protocol('WM_DELETE_WINDOW', app.on_close)
    root.mainloop()
