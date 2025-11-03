const API_BASE = "";

const state = {
    appointments: [],
    currentDate: new Date(),
    selectedDate: null,
    timezone: "America/Mexico_City",
};

const calendarMonth = document.getElementById("calendar-month");
const calendarSubtitle = document.getElementById("calendar-subtitle");
const calendarGrid = document.getElementById("calendar-grid");
const selectedDateTitle = document.getElementById("selected-date-title");
const selectedDateDetail = document.getElementById("selected-date-detail");
const selectedDateAppointments = document.getElementById("selected-date-appointments");
const appointmentsList = document.getElementById("appointments-list");
const currentDateBanner = document.getElementById("current-date");
const timezoneDatetime = document.getElementById("timezone-datetime");
const timezoneDescription = document.getElementById("timezone-description");
const timezoneSelect = document.getElementById("timezone");
const statusFilter = document.getElementById("status-filter");
const appointmentForm = document.getElementById("appointment-form");
const patientInput = document.getElementById("patient-name");
const doctorInput = document.getElementById("doctor-name");
const specialtySelect = document.getElementById("specialty");
const dateInput = document.getElementById("appointment-date");
const timeInput = document.getElementById("appointment-time");
const notesInput = document.getElementById("appointment-notes");
const submitButton = appointmentForm.querySelector("button[type='submit']");

const DAYS_OF_WEEK = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
const STATUS_CLASSES = {
    Pendiente: "status-pendiente",
    Completada: "status-completada",
    Cancelada: "status-cancelada",
};

const HOLIDAYS = {
    "01-01": "Año Nuevo",
    "02-05": "Día de la Constitución",
    "03-21": "Natalicio de Benito Juárez",
    "05-01": "Día del Trabajo",
    "09-16": "Independencia de México",
    "11-20": "Revolución Mexicana",
    "12-25": "Navidad",
};

function showAlert(message) {
    window.alert(message);
}

function confirmAction(message) {
    return window.confirm(message);
}

function getHolidayInfo(dateString) {
    if (!dateString) {
        return null;
    }
    const date = new Date(dateString);
    if (Number.isNaN(date.getTime())) {
        return null;
    }
    const key = `${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
    const holidayName = HOLIDAYS[key];
    return holidayName ? { key, name: holidayName } : null;
}

function isFutureDateTime(dateValue, timeValue) {
    const datetime = new Date(`${dateValue}T${timeValue}`);
    if (Number.isNaN(datetime.getTime())) {
        return false;
    }
    return datetime.getTime() >= Date.now();
}

function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

function parseDateKey(dateKey) {
    const [year, month, day] = dateKey.split("-").map(Number);
    return new Date(year, month - 1, day);
}

function formatDisplayDate(isoString) {
    const date = new Date(isoString);
    return new Intl.DateTimeFormat("es-MX", {
        dateStyle: "full",
    }).format(date);
}

function formatDateTime(isoString) {
    const date = new Date(isoString);
    return new Intl.DateTimeFormat("es-MX", {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(date);
}

function groupAppointmentsByDate() {
    return state.appointments.reduce((acc, appointment) => {
        const dateKey = appointment.fecha.split("T")[0];
        if (!acc[dateKey]) {
            acc[dateKey] = [];
        }
        acc[dateKey].push(appointment);
        return acc;
    }, {});
}

function renderCalendar() {
    const { currentDate } = state;
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDayOfMonth = new Date(year, month, 1);
    const lastDayOfMonth = new Date(year, month + 1, 0);
    const previousMonthLastDay = new Date(year, month, 0).getDate();

    calendarMonth.textContent = firstDayOfMonth.toLocaleDateString("es-MX", {
        month: "long",
        year: "numeric",
    });

    const appointmentsByDate = groupAppointmentsByDate();
    calendarSubtitle.textContent = `${state.appointments.length} citas programadas en ${calendarMonth.textContent}`;

    calendarGrid.innerHTML = "";

    DAYS_OF_WEEK.forEach((day) => {
        const label = document.createElement("div");
        label.className = "calendar-day day-label";
        label.textContent = day;
        calendarGrid.appendChild(label);
    });

    const startDay = firstDayOfMonth.getDay();
    for (let i = 0; i < startDay; i += 1) {
        const dayNumber = previousMonthLastDay - startDay + i + 1;
        const cell = createDayCell({
            dayNumber,
            dateKey: null,
            inactive: true,
            appointments: [],
        });
        calendarGrid.appendChild(cell);
    }

    const daysInMonth = lastDayOfMonth.getDate();
    for (let day = 1; day <= daysInMonth; day += 1) {
        const date = new Date(year, month, day);
        const dateKey = formatDate(date);
        const appointments = appointmentsByDate[dateKey] || [];
        const cell = createDayCell({
            dayNumber: day,
            dateKey,
            inactive: false,
            appointments,
        });
        calendarGrid.appendChild(cell);
    }

    const totalCells = startDay + daysInMonth + DAYS_OF_WEEK.length; // including headers
    const requiredRows = Math.ceil(totalCells / 7);
    const totalSlots = requiredRows * 7;
    const additionalCells = totalSlots - totalCells;

    for (let i = 1; i <= additionalCells; i += 1) {
        const cell = createDayCell({
            dayNumber: i,
            dateKey: null,
            inactive: true,
            appointments: [],
        });
        calendarGrid.appendChild(cell);
    }
}

function createDayCell({ dayNumber, dateKey, inactive, appointments }) {
    const cell = document.createElement("div");
    cell.className = "calendar-day";
    if (inactive) {
        cell.classList.add("inactive");
    }
    if (dateKey && state.selectedDate === dateKey) {
        cell.classList.add("selected");
    }

    const dayNumberWrapper = document.createElement("div");
    dayNumberWrapper.className = "day-number";

    const dayNumberElement = document.createElement("span");
    dayNumberElement.textContent = dayNumber;
    dayNumberWrapper.appendChild(dayNumberElement);

    if (appointments.length) {
        const badge = document.createElement("span");
        badge.className = "appointments-count";
        badge.textContent = `${appointments.length} citas`;
        dayNumberWrapper.appendChild(badge);
    }

    cell.appendChild(dayNumberWrapper);

    appointments.slice(0, 2).forEach((appointment) => {
        const pill = document.createElement("span");
        pill.className = "appointment-pill";
        pill.textContent = `${new Date(appointment.fecha).toLocaleTimeString("es-MX", {
            hour: "2-digit",
            minute: "2-digit",
        })} · ${appointment.paciente}`;
        cell.appendChild(pill);
    });

    if (!inactive && dateKey) {
        cell.addEventListener("click", () => {
            state.selectedDate = dateKey;
            renderCalendar();
            renderSelectedAppointments();
        });
    }

    return cell;
}

function renderSelectedAppointments() {
    const dateKey = state.selectedDate;
    if (!dateKey) {
        selectedDateTitle.textContent = "Citas para el día seleccionado";
        selectedDateDetail.textContent = "Selecciona un día para ver las citas programadas";
        selectedDateAppointments.innerHTML = "";
        return;
    }

    const appointmentsByDate = groupAppointmentsByDate();
    const appointments = appointmentsByDate[dateKey] || [];

    selectedDateTitle.textContent = `Citas para ${parseDateKey(dateKey).toLocaleDateString("es-MX", {
        weekday: "long",
        day: "numeric",
        month: "long",
        year: "numeric",
    })}`;

    if (appointments.length === 0) {
        selectedDateDetail.textContent = "No hay citas programadas para este día";
        selectedDateAppointments.innerHTML = "";
        return;
    }

    selectedDateDetail.textContent = `${appointments.length} cita(s) programadas`;
    selectedDateAppointments.innerHTML = "";

    appointments
        .slice()
        .sort((a, b) => new Date(a.fecha) - new Date(b.fecha))
        .forEach((appointment) => {
            selectedDateAppointments.appendChild(createAppointmentCard(appointment));
        });
}

function createAppointmentCard(appointment) {
    const template = document.getElementById("appointment-card-template");
    const node = template.content.firstElementChild.cloneNode(true);

    node.querySelector(".patient").textContent = appointment.paciente;
    const statusElement = node.querySelector(".status");
    statusElement.textContent = appointment.estado;
    statusElement.classList.add(STATUS_CLASSES[appointment.estado] || "");

    const doctorLine = [appointment.medico, appointment.especialidad]
        .filter(Boolean)
        .join(" · ");
    node.querySelector(".doctor").textContent = doctorLine || "Sin información de doctor";
    node.querySelector(".date").textContent = formatDateTime(appointment.fecha);
    node.querySelector(".notes").textContent = appointment.motivo || "Sin motivo registrado";

    const tagsContainer = node.querySelector(".tags");
    if (appointment.especialidad) {
        const tag = document.createElement("span");
        tag.className = "tag";
        tag.textContent = appointment.especialidad;
        tagsContainer.appendChild(tag);
    }

    const completeButton = node.querySelector(".complete");
    const cancelButton = node.querySelector(".cancel");
    const deleteButton = node.querySelector(".delete");

    completeButton.addEventListener("click", () => updateAppointmentStatus(appointment, "Completada"));
    cancelButton.addEventListener("click", () => updateAppointmentStatus(appointment, "Cancelada"));
    deleteButton.addEventListener("click", () => deleteAppointment(appointment));

    return node;
}

function renderAppointmentsList() {
    const filterValue = statusFilter.value;
    appointmentsList.innerHTML = "";

    const filtered = state.appointments.filter((appointment) =>
        filterValue === "todos" ? true : appointment.estado === filterValue,
    );

    if (filtered.length === 0) {
        const empty = document.createElement("p");
        empty.textContent = "No hay citas que coincidan con el filtro seleccionado.";
        empty.className = "empty-state";
        appointmentsList.appendChild(empty);
        return;
    }

    filtered
        .slice()
        .sort((a, b) => new Date(a.fecha) - new Date(b.fecha))
        .forEach((appointment) => appointmentsList.appendChild(createAppointmentCard(appointment)));
}

async function fetchAppointments() {
    try {
        const response = await fetch(`${API_BASE}/citas`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar las citas");
        }
        const data = await response.json();
        state.appointments = data.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));

        if (!state.selectedDate) {
            const referenceDate = state.currentDate || new Date();
            state.selectedDate = formatDate(referenceDate);
        }

        renderCalendar();
        renderSelectedAppointments();
        renderAppointmentsList();
    } catch (error) {
        console.error(error);
        showAlert("No se pudieron cargar las citas. Intenta nuevamente.");
    }
}

async function updateAppointmentStatus(appointment, status) {
    if (!confirmAction(`¿Deseas marcar la cita de ${appointment.paciente} como ${status.toLowerCase()}?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/citas/${appointment.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ estado: status, timezone: appointment.timezone || state.timezone }),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail?.mensaje || "No se pudo actualizar la cita");
        }

        await fetchAppointments();
        showAlert(`La cita se marcó como ${status.toLowerCase()}.`);
    } catch (error) {
        console.error(error);
        showAlert(error.message);
    }
}

async function deleteAppointment(appointment) {
    if (!confirmAction(`¿Deseas eliminar la cita de ${appointment.paciente}?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/citas/${appointment.id}`, {
            method: "DELETE",
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail?.mensaje || "No se pudo eliminar la cita");
        }

        await fetchAppointments();
        showAlert("La cita se eliminó correctamente.");
    } catch (error) {
        console.error(error);
        showAlert(error.message);
    }
}

async function handleFormSubmit(event) {
    event.preventDefault();

    const paciente = patientInput.value.trim();
    const medico = doctorInput.value.trim();
    const especialidad = specialtySelect.value;
    const fecha = dateInput.value;
    const hora = timeInput.value;
    const motivo = notesInput.value.trim();

    if (!paciente || paciente.length < 3) {
        showAlert("Ingresa el nombre del paciente (mínimo 3 caracteres).");
        patientInput.focus();
        return;
    }

    if (!medico || medico.length < 3) {
        showAlert("Ingresa el nombre del doctor (mínimo 3 caracteres).");
        doctorInput.focus();
        return;
    }

    if (!especialidad) {
        showAlert("Selecciona una especialidad médica para la cita.");
        specialtySelect.focus();
        return;
    }

    if (!fecha) {
        showAlert("Selecciona la fecha de la cita.");
        dateInput.focus();
        return;
    }

    if (!hora) {
        showAlert("Selecciona la hora de la cita.");
        timeInput.focus();
        return;
    }

    if (!isFutureDateTime(fecha, hora)) {
        showAlert("La fecha y hora deben ser posteriores al momento actual.");
        return;
    }

    const holidayInfo = getHolidayInfo(`${fecha}T00:00:00`);
    if (holidayInfo) {
        showAlert(`No se pueden registrar citas en ${holidayInfo.name}. Elige otro día.`);
        dateInput.focus();
        return;
    }

    if (!motivo || motivo.length < 5) {
        showAlert("Describe el motivo de la consulta (mínimo 5 caracteres).");
        notesInput.focus();
        return;
    }

    const payload = {
        paciente,
        medico,
        especialidad,
        fecha: `${fecha}T${hora}`,
        motivo,
        timezone: state.timezone,
    };

    try {
        submitButton.disabled = true;
        submitButton.textContent = "Agendando...";

        const response = await fetch(`${API_BASE}/citas`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail?.mensaje || "No se pudo agendar la cita");
        }

        appointmentForm.reset();
        state.selectedDate = payload.fecha.split("T")[0];
        await fetchAppointments();
        renderCalendar();
        renderSelectedAppointments();
        showAlert("La cita se registró correctamente.");
    } catch (error) {
        console.error(error);
        showAlert(error.message);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Agendar Cita";
    }
}

async function refreshCurrentTime(updateCalendar = false) {
    try {
        const response = await fetch(`${API_BASE}/time/current?timezone=${state.timezone}`);
        if (!response.ok) {
            throw new Error("No disponible");
        }
        const data = await response.json();
        timezoneDatetime.textContent = `${data.date} · ${data.time}`;
        timezoneDescription.textContent = `Zona horaria: ${data.timezone}`;
        currentDateBanner.textContent = formatDisplayDate(data.datetime);

        const remoteDate = new Date(data.datetime);
        if (!Number.isNaN(remoteDate.getTime())) {
            state.currentDate = remoteDate;
            if (updateCalendar) {
                state.selectedDate = formatDate(remoteDate);
                renderCalendar();
                renderSelectedAppointments();
            } else if (!state.selectedDate) {
                state.selectedDate = formatDate(remoteDate);
            }
        }
    } catch (error) {
        timezoneDatetime.textContent = "No disponible";
        timezoneDescription.textContent = "No se pudo obtener la hora actual";
    }
}

function setupNavigation() {
    document.getElementById("prev-month").addEventListener("click", () => {
        state.currentDate.setMonth(state.currentDate.getMonth() - 1);
        renderCalendar();
    });

    document.getElementById("next-month").addEventListener("click", () => {
        state.currentDate.setMonth(state.currentDate.getMonth() + 1);
        renderCalendar();
    });

    document.querySelectorAll(".tab-button").forEach((button) => {
        button.addEventListener("click", () => {
            document.querySelectorAll(".tab-button").forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");
            if (button.dataset.view === "calendar") {
                document.getElementById("calendar-view").classList.remove("hidden");
                document.getElementById("list-view").classList.add("hidden");
            } else {
                document.getElementById("list-view").classList.remove("hidden");
                document.getElementById("calendar-view").classList.add("hidden");
            }
        });
    });
}

function setupEventListeners() {
    appointmentForm.addEventListener("submit", handleFormSubmit);
    timezoneSelect.addEventListener("change", async (event) => {
        state.timezone = event.target.value;
        await refreshCurrentTime(true);
        showAlert(`Zona horaria actualizada a ${event.target.options[event.target.selectedIndex].textContent}.`);
    });
    statusFilter.addEventListener("change", renderAppointmentsList);
}

async function init() {
    setupNavigation();
    setupEventListeners();
    await refreshCurrentTime(true);
    await fetchAppointments();
    setInterval(() => {
        refreshCurrentTime();
    }, 60_000);
}

init().catch((error) => {
    console.error(error);
});
