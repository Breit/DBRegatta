document.addEventListener(
  'DOMContentLoaded',
  function() {
    var calendarEl = document.getElementById('full-calendar');
    const calendarData = JSON.parse(document.getElementById('calendar-data').textContent);

    var calendar = new FullCalendar.Calendar(
      calendarEl,
      {
        themeSystem: 'bootstrap5',
        locale: calendarData.meta.locale,
        height: "100%",
        expandRows: true,
        firstDay: calendarData.meta.firstDay,
        initialView: calendarData.meta.initialView,
        weekNumbers: calendarData.meta.weekNumbers,
        weekText: calendarData.meta.weekText,
        eventSources: calendarData.events,
        headerToolbar: {
          right: 'today,prev,next',
          center: 'title',
          left: 'multiMonthYear,dayGridMonth,timeGridWeek,timeGridDay'
        },
        buttonText: {
          today: calendarData.meta.buttonText.today,
          year: calendarData.meta.buttonText.year,
          month: calendarData.meta.buttonText.month,
          week: calendarData.meta.buttonText.week,
          day: calendarData.meta.buttonText.day
        },
        eventTimeFormat: {
          hour: '2-digit',
          minute: '2-digit',
          meridiem: false
        },
        businessHours: {
          daysOfWeek: [ 1, 2, 3, 4, 5 ],
          startTime: calendarData.meta.trainingStart,
          endTime: calendarData.meta.trainingEnd
        }
      }
    );
    calendar.render();
  }
);
