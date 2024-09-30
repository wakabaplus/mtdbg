#include <tk/tkernel.h>
#include <tm/tmonitor.h>

#include "mtdbg/mtdbg.h"

EXPORT INT usermain(void)
{
    LOCAL ID mtdbg_id;
    LOCAL T_CTSK mtdbg_tsk = {
        .itskpri = 20,
        .stksz = 1024,
        .task = dbg_server,
        .tskatr = TA_HLNG | TA_RNG0,
    };
    mtdbg_id = tk_cre_tsk(&mtdbg_tsk);
    if (mtdbg_id != E_NOMEM)
    {
        tk_sta_tsk(mtdbg_id, 0);
        tk_slp_tsk(TMO_FEVR);
    }
    else
    {
        tm_printf((UB *)"Failed to run debug-server task.");
    }
    return 0;
}