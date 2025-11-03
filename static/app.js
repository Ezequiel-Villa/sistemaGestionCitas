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
const alertContainer = document.getElementById("alert-container");

const DAYS_OF_WEEK = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
const STATUS_CLASSES = {
    Pendiente: "status-pendiente",
    Completada: "status-completada",
    Cancelada: "status-cancelada",
};

const MONTH_SHORT_NAMES = [
    "ene",
    "feb",
    "mar",
    "abr",
    "may",
    "jun",
    "jul",
    "ago",
    "sep",
    "oct",
    "nov",
    "dic",
];

const HOLIDAYS = {
    "01-01": "Año Nuevo",
    "02-05": "Día de la Constitución",
    "03-21": "Natalicio de Benito Juárez",
    "05-01": "Día del Trabajo",
    "09-16": "Independencia de México",
    "11-20": "Revolución Mexicana",
    "12-25": "Navidad",
};

function removeAlert(alertElement) {
    if (!alertElement) {
        return;
    }
    const timeoutId = alertElement.dataset.timeoutId;
    if (timeoutId) {
        window.clearTimeout(Number(timeoutId));
    }
    alertElement.classList.remove("show");
    alertElement.classList.add("hide");
    alertElement.addEventListener(
        "transitionend",
        () => {
            alertElement.remove();
        },
        { once: true },
    );
}

function showAlert(message, type = "info") {
    if (!alertContainer) {
        window.alert(message);
        return;
    }

    const alertElement = document.createElement("div");
    alertElement.className = `alert alert-${type}`;

    const messageElement = document.createElement("span");
    messageElement.className = "alert-message";
    messageElement.textContent = message;

    const closeButton = document.createElement("button");
    closeButton.type = "button";
    closeButton.className = "alert-close";
    closeButton.setAttribute("aria-label", "Cerrar alerta");
    closeButton.innerHTML = "&times;";
    closeButton.addEventListener("click", () => removeAlert(alertElement));

    alertElement.appendChild(messageElement);
    alertElement.appendChild(closeButton);
    alertContainer.appendChild(alertElement);

    requestAnimationFrame(() => {
        alertElement.classList.add("show");
    });

    const timeoutId = window.setTimeout(() => removeAlert(alertElement), 6000);
    alertElement.dataset.timeoutId = String(timeoutId);
}

function confirmAction(message) {
    return window.confirm(message);
}

function parseISODateParts(isoString) {
    if (!isoString || typeof isoString !== "string") {
        return null;
    }

    const [datePart, timePartRaw = ""] = isoString.split("T");
    if (!datePart) {
        return null;
    }

    const [year, month, day] = datePart.split("-").map(Number);
    const cleanTime = timePartRaw.replace("Z", "").split(/[+-]/)[0];
    const [hour = "0", minute = "0"] = cleanTime.split(":");

    const parsed = {
        year,
        month,
        day,
        hour: Number(hour),
        minute: Number(minute),
    };

    if (Object.values(parsed).some((value) => Number.isNaN(value))) {
        return null;
    }

    return parsed;
}

function getAppointmentDateKey(isoString) {
    const parts = parseISODateParts(isoString);
    if (!parts) {
        return null;
    }
    const year = String(parts.year).padStart(4, "0");
    const month = String(parts.month).padStart(2, "0");
    const day = String(parts.day).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

function formatAppointmentTime(isoString) {
    const parts = parseISODateParts(isoString);
    if (!parts) {
        return "--";
    }

    const { hour, minute } = parts;
    const suffix = hour >= 12 ? "p.m." : "a.m.";
    const hour12 = ((hour + 11) % 12) + 1;
    return `${hour12}:${String(minute).padStart(2, "0")} ${suffix}`;
}

function formatAppointmentDateTime(isoString) {
    const parts = parseISODateParts(isoString);
    if (!parts) {
        return "Fecha no disponible";
    }

    const monthName = MONTH_SHORT_NAMES[parts.month - 1] || "";
    return `${parts.day} ${monthName} ${parts.year}, ${formatAppointmentTime(isoString)}`;
}

function compareAppointmentsByDate(a, b) {
    return a.fecha.localeCompare(b.fecha);
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

function formatDisplayDate(isoString, timezone) {
    if (!isoString) {
        return "--";
    }
    const date = new Date(isoString);
    return new Intl.DateTimeFormat("es-MX", {
        dateStyle: "full",
        timeZone: timezone,
    }).format(date);
}

function groupAppointmentsByDate() {
    return state.appointments.reduce((acc, appointment) => {
        const dateKey = getAppointmentDateKey(appointment.fecha);
        if (!dateKey) {
            return acc;
        }
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
        badge.textContent = `${appointments.length}`;
        badge.setAttribute(
            "aria-label",
            appointments.length === 1
                ? "1 cita programada"
                : `${appointments.length} citas programadas`,
        );
        dayNumberWrapper.appendChild(badge);
    }

    cell.appendChild(dayNumberWrapper);

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
    const appointments = (appointmentsByDate[dateKey] || []).slice().sort(compareAppointmentsByDate);

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

    appointments.forEach((appointment) => {
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
    node.querySelector(".date").textContent = formatAppointmentDateTime(appointment.fecha);
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
        .sort(compareAppointmentsByDate)
        .forEach((appointment) => appointmentsList.appendChild(createAppointmentCard(appointment)));
}

async function fetchAppointments() {
    try {
        const response = await fetch(`${API_BASE}/citas`);
        if (!response.ok) {
            throw new Error("No se pudieron cargar las citas");
        }
        const data = await response.json();
        state.appointments = data.sort(compareAppointmentsByDate);

        if (!state.selectedDate) {
            const referenceDate = state.currentDate || new Date();
            state.selectedDate = formatDate(referenceDate);
        }

        renderCalendar();
        renderSelectedAppointments();
        renderAppointmentsList();
    } catch (error) {
        console.error(error);
        showAlert("No se pudieron cargar las citas. Intenta nuevamente.", "error");
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
        showAlert(`La cita se marcó como ${status.toLowerCase()}.`, "success");
    } catch (error) {
        console.error(error);
        showAlert(error.message, "error");
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
        showAlert("La cita se eliminó correctamente.", "success");
    } catch (error) {
        console.error(error);
        showAlert(error.message, "error");
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
        showAlert("Ingresa el nombre del paciente (mínimo 3 caracteres).", "warning");
        patientInput.focus();
        return;
    }

    if (!medico || medico.length < 3) {
        showAlert("Ingresa el nombre del doctor (mínimo 3 caracteres).", "warning");
        doctorInput.focus();
        return;
    }

    if (!especialidad) {
        showAlert("Selecciona una especialidad médica para la cita.", "warning");
        specialtySelect.focus();
        return;
    }

    if (!fecha) {
        showAlert("Selecciona la fecha de la cita.", "warning");
        dateInput.focus();
        return;
    }

    if (!hora) {
        showAlert("Selecciona la hora de la cita.", "warning");
        timeInput.focus();
        return;
    }

    if (!isFutureDateTime(fecha, hora)) {
        showAlert("La fecha y hora deben ser posteriores al momento actual.", "warning");
        return;
    }

    const holidayInfo = getHolidayInfo(`${fecha}T00:00:00`);
    if (holidayInfo) {
        showAlert(`No se pueden registrar citas en ${holidayInfo.name}. Elige otro día.`, "warning");
        dateInput.focus();
        return;
    }

    if (!motivo || motivo.length < 5) {
        showAlert("Describe el motivo de la consulta (mínimo 5 caracteres).", "warning");
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
        state.selectedDate = getAppointmentDateKey(payload.fecha) || payload.fecha.split("T")[0];
        await fetchAppointments();
        renderCalendar();
        renderSelectedAppointments();
        showAlert("La cita se registró correctamente.", "success");
    } catch (error) {
        console.error(error);
        showAlert(error.message, "error");
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
        const timezone = data.timezone || state.timezone;
        const dateKey = data.date;

        timezoneDatetime.textContent = dateKey && data.time ? `${dateKey} · ${data.time}` : "--";
        timezoneDescription.textContent = `Zona horaria: ${timezone}`;
        currentDateBanner.textContent = formatDisplayDate(data.datetime, timezone);

        if (dateKey) {
            const remoteDate = parseDateKey(dateKey);
            if (!Number.isNaN(remoteDate.getTime())) {
                state.currentDate = remoteDate;
                if (updateCalendar) {
                    state.selectedDate = dateKey;
                    renderCalendar();
                    renderSelectedAppointments();
                } else if (!state.selectedDate) {
                    state.selectedDate = dateKey;
                }
            }
        }
    } catch (error) {
        timezoneDatetime.textContent = "No disponible";
        timezoneDescription.textContent = "No se pudo obtener la hora actual";
        currentDateBanner.textContent = "--";
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
        showAlert(
            `Zona horaria actualizada a ${event.target.options[event.target.selectedIndex].textContent}.`,
            "info",
        );
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
