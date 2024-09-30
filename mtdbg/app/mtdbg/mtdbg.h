#ifndef MTDBG_H
#define MTDBG_H

#include <tk/tkernel.h>
IMPORT void dbg_server(INT stacd, void *exinf);

#define TASK_LIST_MAGIC (UB *)"OK_T"
#define TASK_STATUS_MAGIC (UB *)"OK_t"
#define SEND_DONE_MAGIC (UB *)"DONE"

#endif