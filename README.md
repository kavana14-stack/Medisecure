# 🔐 MediSecure — Secure Clinic Management System

> A Django-based secure clinic management system designed to protect sensitive medical information using applied cryptography.

MediSecure is a web-based clinic management system that connects **patients, doctors, and administrators** while integrating cryptographic security into the management of medical records and prescriptions.

The system focuses on three core security properties:

- 🔒 **Confidentiality** — AES-256-GCM
- ✍️ **Authenticity** — Ed25519 Digital Signatures
- 🔗 **Integrity** — SHA-3-256 Hashing

---

## 🎯 Project Overview

Healthcare applications handle highly sensitive information such as diagnoses, clinical notes, prescriptions, and patient details.

MediSecure addresses this problem by combining normal clinic-management functionality with practical security mechanisms.

The system provides:

- Patient registration and authentication
- Doctor authentication and role-based access
- Appointment booking and management
- Secure medical-record creation
- Encrypted medical diagnoses
- Digitally signed prescriptions
- Prescription signature verification
- Medical-record integrity verification
- SHA-3 hash-chain verification
- Dedicated Security Center

---

## 🛡️ Security Architecture

MediSecure uses three cryptographic mechanisms, each serving a different security purpose.

### 🔒 1. AES-256-GCM — Confidentiality

Sensitive medical diagnoses are encrypted before being stored in the database.

**Process:**

```text
Medical Diagnosis
       ↓
AES-256-GCM Encryption
       ↓
Nonce + Ciphertext
       ↓
Database
