function select_filter(team_id, skipper_id)
{
  const csrftoken = getCookie('csrftoken');
  var data = {};
  data['selectedTeamId'] = team_id;
  data['selectedSkipperId'] = skipper_id;

  $.post(
    {
      url: window.location.href,
      data: data,
      headers: { 'X-CSRFToken': csrftoken }
    },
    function(data, status)
    {
      if (status === 'success')
      {
        $('.menu').html($(data).find('.menu').html());
        $('#calendar-data').html($(data).filter('#calendar-data').html());
        $('#filter-selector').html($(data).find('#filter-selector').html());

        show_calendar();
      }
    }
  );
}

function show_calendar() {
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
      },
      eventDidMount: function(info)
      {
        if ('title' in info.event && info.event.title)
        {
          let tooltip_text = '<p>';
          tooltip_text += '<span class="lead">' + info.event.title + '</span>';
          tooltip_text += '<br>';
          if ('extendedProps' in info.event)
          {
            if ('company' in info.event.extendedProps && info.event.extendedProps.company) {
              tooltip_text += info.event.extendedProps.company;
            }
            tooltip_text += '</p><p>';
            if ('timeslot' in info.event.extendedProps && info.event.extendedProps.timeslot) {
              tooltip_text += info.event.start.toLocaleDateString();
              tooltip_text += '<br>';
              tooltip_text += '<i>' + info.event.extendedProps.timeslot + '</i>';
            }
            if ('skipper' in info.event.extendedProps && info.event.extendedProps.skipper) {
              tooltip_text += '</p><p><b>' + info.event.extendedProps.skipper + '</b>';
            }
            if ('note' in info.event.extendedProps && info.event.extendedProps.note) {
              tooltip_text += '</p><p>' + info.event.extendedProps.note;
            }
          }
          else
          {
            tooltip_text += info.event.start.toLocaleDateString();
            tooltip_text += '<br>';
            tooltip_text += '<i>' + info.event.start.toLocaleTimeString() + '</i>';
          }
          tooltip_text += '</p>';

          var tooltip = new bootstrap.Tooltip(
            info.el,
            {
              title: tooltip_text,
              placement: 'top',
              trigger: 'hover',
              container: 'body',
              html: true,
              customClass: 'tooltip-text-left'
            }
          );
        }
      }
    }
  );
  calendar.render();

  const resizeObserver = new ResizeObserver(
    () => {
      calendar.updateSize();
    }
  );
  resizeObserver.observe(calendarEl);
}

document.addEventListener(
  'DOMContentLoaded',
  show_calendar
);
