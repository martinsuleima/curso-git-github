import os
from abc import ABC, abstractmethod
from collections import deque

# ==========================================
# PARTE 1: JERARQUÍA DE PROGRAMAS (POLIMORFISMO)
# ==========================================

class ProgramaAcademico(ABC):
    def __init__(self, nombre_programa):
        self.nombre_programa = nombre_programa

    def calcular_promedio(self, notas):
        if not notas:
            return 0.0
        return sum(notas) / len(notas)

    @abstractmethod
    def esta_aprobado(self, notas):
        """Método abstracto sobrescrito en cada modalidad."""
        pass


class Curso(ProgramaAcademico):
    def __init__(self):
        super().__init__("Curso")

    def esta_aprobado(self, notas):
        # Regla: Promedio >= 10/20
        return self.calcular_promedio(notas) >= 10.0


class Diplomado(ProgramaAcademico):
    def __init__(self):
        super().__init__("Diplomado")

    def esta_aprobado(self, notas):
        # Regla: Promedio >= 14/20
        return self.calcular_promedio(notas) >= 14.0


class Bootcamp(ProgramaAcademico):
    def __init__(self):
        super().__init__("Bootcamp")

    def esta_aprobado(self, notas):
        # Regla: Ninguna nota individual menor a 14/20 y requiere al menos 1 nota
        if not notas:
            return False
        return all(nota >= 14.0 for nota in notas)


def obtener_instancia_programa(tipo_str):
    """Factory Helper para instanciar el programa correcto según texto."""
    tipo_clean = tipo_str.strip().capitalize()
    if tipo_clean == "Curso":
        return Curso()
    elif tipo_clean == "Diplomado":
        return Diplomado()
    elif tipo_clean == "Bootcamp":
        return Bootcamp()
    else:
        return Curso()


# ==========================================
# PARTE 2: JERARQUÍA DE PERSONAS
# ==========================================

class Persona:
    def __init__(self, cedula, nombre, correo):
        self.cedula = cedula.strip()
        self.nombre = nombre.strip()
        self.correo = correo.strip()


class Alumno(Persona):
    def __init__(self, cedula, nombre, correo, programa_obj, notas=None):
        super().__init__(cedula, nombre, correo)
        self.programa = programa_obj  # Instancia de ProgramaAcademico
        self.notas = notas if notas is not None else []

    def agregar_nota(self, nota):
        if len(self.notas) < 3:
            self.notas.append(nota)
            return True
        return False

    def obtener_promedio(self):
        return self.programa.calcular_promedio(self.notas)

    def es_aprobado(self):
        return self.programa.esta_aprobado(self.notas)


class Profesor(Persona):
    def __init__(self, cedula, nombre, correo, especialidad, materia):
        super().__init__(cedula, nombre, correo)
        self.especialidad = especialidad.strip()
        self.materia = materia.strip()


# ==========================================
# PARTE 3: GESTOR DEL SISTEMA (LÓGICA Y PERSISTENCIA)
# ==========================================

class SGA_Sistema:
    ARCH_ALUMNOS = "alumnos.txt"
    ARCH_PROFESORES = "profesores.txt"
    ARCH_CERTIFICADOS = "certificados_pendientes.txt"

    def __init__(self):
        self.alumnos = {}    # Diccionario {cedula: objeto Alumno}
        self.profesores = {} # Diccionario {cedula: objeto Profesor}
        self.pila_notas = [] # Pila (Stack / LIFO) para CTRL+Z: guarda tuplas (cedula_alumno, nota_agregada)
        
        self.cargar_datos()

    # --- CARGA Y PERSISTENCIA DIRECTA ---

    def cargar_datos(self):
        # Cargar Alumnos
        if os.path.exists(self.ARCH_ALUMNOS):
            with open(self.ARCH_ALUMNOS, "r", encoding="utf-8") as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    partes = [p.strip() for p in linea.split(",")]
                    if len(partes) >= 4:
                        ced, nom, cor, prog_str = partes[0], partes[1], partes[2], partes[3]
                        notas = []
                        if len(partes) > 4:
                            for n in partes[4:]:
                                try:
                                    val = float(n)
                                    if val > 0: # Ignorar ceros de relleno iniciales
                                        notas.append(val)
                                except ValueError:
                                    pass
                        prog_obj = obtener_instancia_programa(prog_str)
                        self.alumnos[ced] = Alumno(ced, nom, cor, prog_obj, notas)

        # Cargar Profesores
        if os.path.exists(self.ARCH_PROFESORES):
            with open(self.ARCH_PROFESORES, "r", encoding="utf-8") as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    partes = [p.strip() for p in linea.split(",")]
                    if len(partes) >= 5:
                        ced, nom, cor, esp, mat = partes[0], partes[1], partes[2], partes[3], partes[4]
                        self.profesores[ced] = Profesor(ced, nom, cor, esp, mat)

    def guardar_alumnos(self):
        with open(self.ARCH_ALUMNOS, "w", encoding="utf-8") as f:
            for alum in self.alumnos.values():
                # Formatear notas a 3 elementos
                notas_str = [str(int(n) if n.is_integer() else n) for n in alum.notas]
                while len(notas_str) < 3:
                    notas_str.append("0")
                
                linea = f"{alum.cedula}, {alum.nombre}, {alum.correo}, {alum.programa.nombre_programa}, " + ", ".join(notas_str) + "\n"
                f.write(linea)

    def guardar_profesores(self):
        with open(self.ARCH_PROFESORES, "w", encoding="utf-8") as f:
            for prof in self.profesores.values():
                linea = f"{prof.cedula}, {prof.nombre}, {prof.correo}, {prof.especialidad}, {prof.materia}\n"
                f.write(linea)

    # --- OPCIONES DEL MENÚ ---

    def registrar_alumno(self):
        print("\n--- REGISTRAR ALUMNO ---")
        cedula = input("Cédula: ").strip()
        if cedula in self.alumnos:
            print("Error: Ya existe un alumno con esa cédula.")
            return

        nombre = input("Nombre Completo: ").strip()
        correo = input("Correo Electrónico: ").strip()
        
        print("Seleccione Tipo de Programa:")
        print("1. Curso")
        print("2. Diplomado")
        print("3. Bootcamp")
        opt = input("Opción (1-3): ").strip()
        
        if opt == "1":
            prog = Curso()
        elif opt == "2":
            prog = Diplomado()
        elif opt == "3":
            prog = Bootcamp()
        else:
            print("Opción inválida. Asignado 'Curso' por defecto.")
            prog = Curso()

        nuevo_alum = Alumno(cedula, nombre, correo, prog)
        self.alumnos[cedula] = nuevo_alum
        self.guardar_alumnos() # Persistencia inmediata
        print(f"¡Alumno {nombre} registrado exitosamente!")

    def registrar_profesor(self):
        print("\n--- REGISTRAR PROFESOR ---")
        cedula = input("Cédula: ").strip()
        if cedula in self.profesores:
            print("Error: Ya existe un profesor con esa cédula.")
            return

        nombre = input("Nombre Completo: ").strip()
        correo = input("Correo Electrónico: ").strip()
        especialidad = input("Especialidad Académica: ").strip()
        materia = input("Materia Asignada: ").strip()

        nuevo_prof = Profesor(cedula, nombre, correo, especialidad, materia)
        self.profesores[cedula] = nuevo_prof
        self.guardar_profesores() # Persistencia inmediata
        print(f"¡Profesor {nombre} registrado exitosamente!")

    def registrar_nota_alumno(self):
        print("\n--- REGISTRAR NOTA A UN ALUMNO ---")
        cedula = input("Ingrese Cédula del Alumno: ").strip()
        
        if cedula not in self.alumnos:
            print("Error: Alumno no encontrado.")
            return

        alumno = self.alumnos[cedula]
        if len(alumno.notas) >= 3:
            print(f"El alumno {alumno.nombre} ya tiene el máximo de 3 notas registradas.")
            return

        try:
            nota = float(input("Ingrese calificación (0 - 20): "))
            if nota < 0 or nota > 20:
                print("Error: La nota debe estar entre 0 y 20.")
                return
        except ValueError:
            print("Error: Ingrese un valor numérico válido.")
            return

        alumno.agregar_nota(nota)
        # Apilar acción en la Pila LIFO
        self.pila_notas.append((cedula, nota))
        self.guardar_alumnos() # Persistencia inmediata
        print(f"¡Nota {nota} añadida a {alumno.nombre} con éxito!")

    def deshacer_ultima_nota(self):
        """Opción 4: Implementación de Pila (LIFO) para CTRL+Z."""
        print("\n--- DESHACER ÚLTIMO REGISTRO DE NOTA (LIFO) ---")
        if not self.pila_notas:
            print("No hay notas recientes en la pila para deshacer.")
            return

        cedula, nota_removida = self.pila_notas.pop() # LIFO
        if cedula in self.alumnos:
            alumno = self.alumnos[cedula]
            if alumno.notas and alumno.notas[-1] == nota_removida:
                alumno.notas.pop()
                self.guardar_alumnos()
                print(f"¡Éxito! Se removió la última nota ({nota_removida}) del alumno {alumno.nombre} [{cedula}].")
            else:
                print("Error: La estructura de notas sufrió inconsistencias externas.")

    def generar_cola_certificados(self):
        """Opción 5: Implementación de Cola (FIFO) y exportación de reporte."""
        print("\n--- GENERAR COLA DE CERTIFICADOS (FIFO) ---")
        cola_graduando = deque()

        # Insertar aprobados en la Cola (Queue)
        for alumno in self.alumnos.values():
            if alumno.es_aprobado():
                cola_graduando.append(alumno)

        total_graduandos = len(cola_graduando)
        print(f"Procesando cola de certificados... Encontrados: {total_graduandos} graduandos.")

        # Exportar procesando en orden FIFO
        with open(self.ARCH_CERTIFICADOS, "w", encoding="utf-8") as f:
            f.write("=========================================\n")
            f.write("   REPORTE DE CERTIFICADOS PENDIENTES    \n")
            f.write("=========================================\n")
            f.write(f"Total de graduandos en cola: {total_graduandos}\n\n")

            contador = 1
            while cola_graduando:
                alum = cola_graduando.popleft() # FIFO
                prom = alum.obtener_promedio()
                
                f.write(f"{contador}. [{alum.cedula}] {alum.nombre}\n")
                f.write(f"   - Programa: {alum.programa.nombre_programa}\n")
                f.write(f"   - Promedio Final: {prom:.1f}\n")
                if isinstance(alum.programa, Bootcamp):
                    f.write("   - Estatus: APROBADO (Cumple regla de ninguna nota < 14)\n")
                else:
                    f.write("   - Estatus: APROBADO\n")
                f.write("\n")
                contador += 1

            f.write("=========================================\n")
            f.write("* Fin del reporte - Generado por SGA-DO *\n")

        print(f"¡Reporte generado con éxito en '{self.ARCH_CERTIFICADOS}'!")

    def mostrar_reporte_general(self):
        print("\n=========================================")
        print("          REPORTE GENERAL SGA-DO         ")
        print("=========================================")
        
        print("\n--- PROFESORES ACTIVOS ---")
        if not self.profesores:
            print("No hay profesores registrados.")
        else:
            for p in self.profesores.values():
                print(f"• [{p.cedula}] {p.nombre} | Especialidad: {p.especialidad} | Materia: {p.materia}")

        print("\n--- ALUMNOS REGISTRADOS ---")
        if not self.alumnos:
            print("No hay alumnos registrados.")
        else:
            for a in self.alumnos.values():
                prom = a.obtener_promedio()
                estatus = "APROBADO" if a.es_aprobado() else "REPROBADO"
                notas_str = ", ".join(map(str, a.notas)) if a.notas else "Sin notas"
                print(f"• [{a.cedula}] {a.nombre} - Prog: {a.programa.nombre_programa} | Notas: [{notas_str}] | Prom: {prom:.1f} | Estatus: {estatus}")

# ==========================================
# PARTE 4: BUCLE PRINCIPAL DE CONSOLA
# ==========================================

def menu_principal():
    sistema = SGA_Sistema()

    while True:
        print("\n=========================================")
        print("    SGA-DO: SISTEMA DIPLOMADOSONLINE     ")
        print("=========================================")
        print("1. Registrar Alumno")
        print("2. Registrar Profesor")
        print("3. Registrar Notas a un Alumno")
        print("4. Deshacer Último Registro de Nota")
        print("5. Generar Cola de Certificados")
        print("6. Mostrar Reporte General")
        print("7. Salir")
        
        opcion = input("Seleccione una opción (1-7): ").strip()

        if opcion == "1":
            sistema.registrar_alumno()
        elif opcion == "2":
            sistema.registrar_profesor()
        elif opcion == "3":
            sistema.registrar_nota_alumno()
        elif opcion == "4":
            sistema.deshacer_ultima_nota()
        elif opcion == "5":
            sistema.generar_cola_certificados()
        elif opcion == "6":
            sistema.mostrar_reporte_general()
        elif opcion == "7":
            print("\nGuardando cambios pendientes y cerrando aplicación... ¡Hasta luego!")
            break
        else:
            print("\n[!] Opción no válida. Por favor, ingrese un número del 1 al 7.")

if __name__ == "__main__":
    menu_principal()