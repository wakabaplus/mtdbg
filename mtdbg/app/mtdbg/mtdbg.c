#include <tk/tkernel.h>
#include <tm/tmonitor.h>
#include <tk/dbgspt.h>
#include <mtkernel/kernel/knlinc/tstdlib.h>
#include "mtdbg/mtdbg.h"

LOCAL void write_uart(void *bin, SZ length)
{
    for (SZ i = 0; i < length; i++)
    {
        tm_putchar(((UB *)bin)[i]);
    }
}

EXPORT void dbg_server(INT stacd, void *exinf)
{
#ifndef TK_SUPPORT_DBGSPT
    tm_printf((UB *)"Please enable TK_SUPPORT_DBGSPT.");
    tk_ext_tsk();
#endif
    libtm_init();
    tm_printf((UB *)"This is mtdbg server. This port is intended to read by mtdbg client.");
    UB MTDBG_MAGIC[] = {0x00, 0xDD, 0xBB, 'G', 0x00};
    write_uart(MTDBG_MAGIC, 6);
    while (1)
    {
        INT query = tm_getchar(1);
        switch (query)
        {
        case 'T':
            tm_printf(TASK_LIST_MAGIC);
            UB sizeof_int = sizeof(INT);
            UB sizeof_ptr = sizeof(void *);
            UB sizeof_pri = sizeof(PRI);
            UB sizeof_uint = sizeof(UINT);
            UB sizeof_id = sizeof(ID);
            UB sizeof_reltim = sizeof(RELTIM);
            UB sizeof_fp = sizeof(FP);
            write_uart(&sizeof_int, sizeof(UB));
            write_uart(&sizeof_ptr, sizeof(UB));
            write_uart(&sizeof_pri, sizeof(UB));
            write_uart(&sizeof_uint, sizeof(UB));
            write_uart(&sizeof_id, sizeof(UB));
            write_uart(&sizeof_reltim, sizeof(UB));
            write_uart(&sizeof_fp, sizeof(UB));
            do
            {
                INT MAX_TASK = 64;
                ID list[MAX_TASK];
                SZ list_size = sizeof(ID) * MAX_TASK;
                knl_memset(list, 0, list_size);
                INT ct = td_lst_tsk(list, MAX_TASK);
                if (ct < 0)
                {
                    tm_printf((UB *)"Err: %d", ct);
                    break;
                }
                write_uart(&ct, sizeof(INT));
                write_uart(&list_size, sizeof(SZ));
                write_uart(&list, list_size);
            } while (0);
            tm_printf(SEND_DONE_MAGIC);
            break;
        case 't':
            tm_printf(TASK_STATUS_MAGIC);
            do
            {
                ID tskid = 0;
                INT input_id = tm_getchar(1);
                tskid = input_id;
                input_id = tm_getchar(1);
                tskid = tskid | (input_id << 8);
                input_id = tm_getchar(1);
                tskid = tskid | (input_id << 16);
                input_id = tm_getchar(1);
                tskid = tskid | (input_id << 24);

                TD_RTSK rtsk;
                INT ercd = td_ref_tsk(tskid, &rtsk);
                if (ercd != E_OK)
                {
                    tm_printf((UB *)"Err: %d", ercd);
                    break;
                }
                UB length = sizeof(TD_RTSK);
                write_uart(&length, sizeof(UB));
                write_uart(&tskid, sizeof(ID));
                write_uart(&ercd, length);
            } while (0);
            tm_printf(SEND_DONE_MAGIC);
            break;
        default:
            tm_printf((UB *)"%d ", query);
        }
    }
}
