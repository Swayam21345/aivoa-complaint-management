import React from 'react';
import { ComplaintStatus } from '../../../types/complaint.types';
import styles from './WorkflowStepper.module.css';

interface WorkflowStepperProps {
  currentStatus: ComplaintStatus;
}

interface StepItem {
  id: string;
  label: string;
  statuses: string[];
}

const WORKFLOW_STEPS: StepItem[] = [
  { id: 'intake', label: '1. Intake', statuses: ['NEW', 'Draft'] },
  { id: 'triage', label: '2. Triage', statuses: ['TRIAGED', 'UNDER_REVIEW'] },
  { id: 'assigned', label: '3. Assigned', statuses: ['ASSIGNED'] },
  { id: 'investigation', label: '4. Investigation', statuses: ['UNDER_INVESTIGATION', 'IN_PROGRESS', 'WAITING_CUSTOMER'] },
  { id: 'root_cause', label: '5. Root Cause', statuses: ['ROOT_CAUSE_IDENTIFIED'] },
  { id: 'capa', label: '6. CAPA', statuses: ['CAPA_IN_PROGRESS'] },
  { id: 'qa_review', label: '7. QA Review', statuses: ['QA_REVIEW'] },
  { id: 'qa_approved', label: '8. QA Approved', statuses: ['QA_APPROVED', 'RESOLVED'] },
  { id: 'closed', label: '9. Closed', statuses: ['CLOSED'] },
];

export const WorkflowStepper: React.FC<WorkflowStepperProps> = ({ currentStatus }) => {
  const isTerminal = ['REJECTED', 'CANCELLED', 'ON_HOLD'].includes(currentStatus);

  // Find index of step matching current status
  const currentStepIndex = WORKFLOW_STEPS.findIndex((step) =>
    step.statuses.includes(currentStatus)
  );

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.title}>TrackWise / Veeva Vault QMS Workflow Engine</span>
        {isTerminal && (
          <span className={`${styles.badge} ${styles[currentStatus.toLowerCase()]}`}>
            {currentStatus.replace('_', ' ')}
          </span>
        )}
      </div>

      <div className={styles.stepperContainer}>
        {WORKFLOW_STEPS.map((step, idx) => {
          let statusClass = styles.pending;

          if (currentStepIndex !== -1) {
            if (idx < currentStepIndex) {
              statusClass = styles.completed;
            } else if (idx === currentStepIndex) {
              statusClass = styles.active;
            }
          }

          return (
            <div key={step.id} className={`${styles.step} ${statusClass}`}>
              <div className={styles.stepCircle}>
                {idx < currentStepIndex ? '✓' : idx + 1}
              </div>
              <span className={styles.stepLabel}>{step.label}</span>
              {idx < WORKFLOW_STEPS.length - 1 && <div className={styles.stepConnector} />}
            </div>
          );
        })}
      </div>
    </div>
  );
};
