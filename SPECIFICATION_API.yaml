# OpenAPI 3.0 Specification

openapi: "3.0.3"
info:
  title: Employee Rating API
  version: "1.0.0"

paths:
  /api/v1/employees:
    get:
      summary: Список сотрудников
      parameters:
        - name: department_id
          in: query
          schema: { type: string, format: uuid }
        - name: is_active
          in: query
          schema: { type: boolean, default: true }
        - name: page
          in: query
          schema: { type: integer, default: 1 }
        - name: size
          in: query
          schema: { type: integer, default: 20, maximum: 100 }
      responses:
        "200":
          content:
            application/json:
              schema: { $ref: "#/components/schemas/EmployeePage" }

  /api/v1/ratings:
    post:
      summary: Создать запись рейтинга
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: "#/components/schemas/RatingEntryCreate" }
    get:
      summary: Получить рейтинги за период
      parameters:
        - name: period_from
          in: query
          required: true
          schema: { type: string, format: date }
        - name: period_to
          in: query
          required: true
          schema: { type: string, format: date }
        - name: department_id
          in: query
          schema: { type: string, format: uuid }

  /api/v1/ratings/snapshots/{period}:
    get:
      summary: Снимок рейтинга за период
      parameters:
        - name: period
          in: path
          required: true
          schema: { type: string, format: date }

  /api/v1/ratings/analytics/trends:
    get:
      summary: Тренды рейтинга сотрудника
      parameters:
        - name: employee_id
          in: query
          required: true
          schema: { type: string, format: uuid }
        - name: months
          in: query
          schema: { type: integer, default: 6 }

  /api/v1/ratings/import:
    post:
      summary: Импорт данных из CSV
      requestBody:
        content:
          multipart/form-data:
            schema:
              properties:
                file: { type: string, format: binary }
                period: { type: string, format: date }

  /api/v1/reports/generate:
    post:
      summary: Запуск генерации отчёта (async)
      requestBody:
        content:
          application/json:
            schema: { $ref: "#/components/schemas/ReportRequest" }
      responses:
        "202":
          content:
            application/json:
              schema:
                properties:
                  task_id: { type: string }
                  status_url: { type: string }

  /api/v1/reports/status/{task_id}:
    get:
      summary: Статус генерации отчёта

