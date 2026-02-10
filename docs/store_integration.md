# Integracion Tienda -> Backend NFC

Este endpoint permite crear o actualizar la configuracion de un NFC cuando se confirma una compra.

## Endpoint
- `POST /api/nfc/configure/`

## Body base
```json
{
  "public_uid": "ABC123",
  "experience_type": "CATEGORY",
  "version": "RVR1909",
  "category": "amor",
  "static_verse_id": null,
  "is_active": true
}
```

## Campos
- `public_uid` (string, requerido)
- `experience_type` (string, requerido) valores: `STATIC`, `CATEGORY`, `STUDY`, `DAILY`
- `version` (string, requerido) ejemplo: `RVR1909`, `KJV`
- `category` (string, requerido si `CATEGORY`) slug de categoria
- `static_verse_id` (int, requerido si `STATIC`)
- `is_active` (bool, opcional, default `true`)

## Reglas de validacion
- La version debe existir.
- `CATEGORY` requiere categoria existente y con versiculos en esa version.
- `STATIC` requiere `static_verse_id` y el versiculo debe pertenecer a la version.
- `STUDY` usa categoria fija `general` y debe existir con versiculos en esa version.
- `DAILY` requiere que la version tenga versiculos cargados.

## Ejemplos

### CATEGORY
```json
{
  "public_uid": "ABC123",
  "experience_type": "CATEGORY",
  "version": "RVR1909",
  "category": "amor"
}
```

### STATIC
```json
{
  "public_uid": "ABC123",
  "experience_type": "STATIC",
  "version": "RVR1909",
  "static_verse_id": 12
}
```

### STUDY
```json
{
  "public_uid": "ABC123",
  "experience_type": "STUDY",
  "version": "RVR1909"
}
```

### DAILY
```json
{
  "public_uid": "ABC123",
  "experience_type": "DAILY",
  "version": "RVR1909"
}
```

## Respuesta
```json
{
  "public_uid": "ABC123",
  "experience_type": "CATEGORY",
  "version": "RVR1909",
  "category": "amor",
  "static_verse_id": null,
  "is_active": true
}
```
