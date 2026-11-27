# QR Attendance System — Story Estimation

## 1. Estimation Method

Planning Poker using the Fibonacci scale: 1, 2, 3, 5, 8, 13.

**Reference Story:** US-10 — View Class Roster.

**Reference Estimate:** 2 Story Points.

**Estimation Approach:** Relative estimation based on implementation complexity, required effort, validation rules, technical dependencies, and potential risks.

## 2. INVEST Review

The following proposed INVEST assessment evaluates each user story against the six INVEST principles.

- **I:** Independent
- **N:** Negotiable
- **V:** Valuable
- **E:** Estimable
- **S:** Small
- **T:** Testable

| Story | I | N | V | E | S | T | Fix Needed |
|---|---|---|---|---|---|---|---|
| US-01 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-02 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-03 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-04 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-05 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-06 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-07 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-08 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-09 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-10 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-11 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-12 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-13 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-14 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |
| US-15 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | None |

### INVEST Review Summary

The stories are designed to deliver identifiable user value, support measurable acceptance criteria, and remain small enough to be completed within a single Sprint. Functional dependencies between authentication, course management, QR sessions, and attendance recording are managed through backlog prioritization.

## 3. Planning Poker Record

The following table represents a simulated Planning Poker session involving three developers, pending team confirmation.

| Story | Round 1 Votes | Round 2 Votes | Final Proposed Points | Key Discussion Point |
|---|---|---|---:|---|
| US-01 | 2, 3, 3 | Not required | 3 | Authentication and role-based access |
| US-02 | 3, 3, 3 | Not required | 3 | Course creation and unique code validation |
| US-03 | 2, 3, 5 | 3, 3, 3 | 3 | Enrollment validation and duplicate prevention |
| US-04 | 3, 3, 5 | 3, 3, 3 | 3 | Session duration and expiration handling |
| US-05 | 1, 2, 2 | Not required | 2 | Unique QR code generation |
| US-06 | 3, 5, 8 | 5, 5, 5 | 5 | Camera compatibility and QR image decoding |
| US-07 | 3, 5, 8 | 5, 5, 5 | 5 | Enrollment, QR token, and session validation |
| US-08 | 2, 3, 3 | Not required | 3 | Reliable attendance persistence |
| US-09 | 3, 3, 3 | Not required | 3 | Attendance history and status display |
| US-10 | 2, 2, 2 | Not required | 2 | Reference story for relative estimation |
| US-11 | 1, 2, 3 | 2, 2, 2 | 2 | Duplicate check-in prevention |
| US-12 | 3, 5, 8 | 5, 5, 5 | 5 | CSV generation and date filtering |
| US-13 | 1, 2, 2 | Not required | 2 | Profile editing and input validation |
| US-14 | 3, 5, 8 | 5, 5, 5 | 5 | Absent-session filtering and correction approval |
| US-15 | 2, 3, 5 | 3, 3, 3 | 3 | Account registration and unique student IDs |
| **Total** | | | **49** | |

## 4. Estimation Summary

| Story Points | Number of Stories | Total Points |
|---|---:|---:|
| 1 | 0 | 0 |
| 2 | 4 | 8 |
| 3 | 7 | 21 |
| 5 | 4 | 20 |
| 8 | 0 | 0 |
| 13 | 0 | 0 |
| **Total** | **15** | **49** |

- **Total User Stories:** 15
- **Total Backlog:** 49 Story Points
- **Minimum Story Estimate:** 2 Story Points
- **Maximum Story Estimate:** 5 Story Points
- **MVP Estimate:** 34 Story Points
- **Post-MVP Estimate:** 15 Story Points

## 5. Estimation Rules

- Developers vote independently using the Fibonacci scale.
- The Product Owner explains the story and its acceptance criteria without voting.
- All votes are revealed simultaneously to prevent anchoring.
- Large differences are discussed before starting another estimation round.
- Stories estimated at 13 points or more must be split into smaller stories before entering a Sprint.
- Agreed estimates are recorded in the Jira Story Points field.
- Estimates represent relative complexity, effort, and uncertainty rather than exact working hours.

## 6. Estimation Reflection

QR scanning, session validation, report generation, and attendance correction received the highest proposed estimates because they involve multiple validation rules, technical dependencies, and error-handling scenarios. Simpler features, such as QR generation, class roster display, and profile editing, received lower estimates.

The simulated Planning Poker discussion demonstrates how different perspectives can be reconciled through clarification and relative estimation. All proposed stories remain below 13 Story Points, making them suitable for Sprint planning. The estimates should be confirmed by the development team and refined using actual Sprint performance.