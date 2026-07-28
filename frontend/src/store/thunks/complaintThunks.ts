// Re-export thunks from complaint slices for convenient import by components.
export {
  submitComplaint,
  fetchComplaintDetail,
  patchComplaintStatus,
} from '@/store/slices/complaintSlice';

export { fetchComplaints } from '@/store/slices/complaintsListSlice';
