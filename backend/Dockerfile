FROM python:3.13-slim

# WeasyPrint 53+ (we're on 69.0, see requirements.txt) renders through its
# own pydyf-based PDF backend and only needs Pango as a native runtime
# dependency for text shaping/layout -- unlike older WeasyPrint releases,
# no Cairo or GDK-Pixbuf is required. See
# https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    fontconfig \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=config.settings.prod
ENV PYTHONUNBUFFERED=1

# migrate/collectstatic run at container start, not build time: prod.py
# requires several secrets (DB, AWS_*) just to import the settings
# module, and those are only guaranteed present in the running
# container's environment, not necessarily during the image build.
CMD python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
