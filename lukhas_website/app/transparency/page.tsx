'use client'

import React,
{
  useState,
  useEffect
}
from 'react'
import {
  Container,
  Typography,
  Card,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Alert,
  Box,
  IconButton,
  Collapse,
  TablePagination,
} from '@mui/material'
import {
  KeyboardArrowDown as KeyboardArrowDownIcon,
  KeyboardArrowUp as KeyboardArrowUpIcon,
} from '@mui/icons-material'

// Based on the AuditEntry dataclass in audit_trail.py
interface AuditEntry {
  audit_id: string
  timestamp: number
  decision_type: string
  decision: string
  confidence: number
  component: string
  user_id ? : string
  reasoning: string
  input_data: Record < string, any >
    output_data: Record < string, any >
    policies: string[]
}

const decisionTypeColors: {
  [key: string]: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'
} = {
  RESPONSE: 'primary',
  MODERATION: 'warning',
  ROUTING: 'info',
  SAFETY: 'error',
  LEARNING: 'success',
  SYSTEM: 'secondary',
  default: 'default',
}

function Row(props: {
  row: AuditEntry
}) {
  const {
    row
  } = props
  const [open, setOpen] = useState(false)

  const color = decisionTypeColors[row.decision_type] || decisionTypeColors.default

  return ( <
    >
    <
    TableRow sx = {
      {
        '& > *': {
          borderBottom: 'unset'
        }
      }
    } >
    <
    TableCell >
    <
    IconButton aria-label = "expand row"
    size = "small"
    onClick = {
      () => setOpen(!open)
    } > {
      open ? < KeyboardArrowUpIcon / > : < KeyboardArrowDownIcon / >
    } <
    /IconButton> <
    /TableCell> <
    TableCell component = "th"
    scope = "row" > {
      new Date(row.timestamp * 1000).toLocaleString()
    } <
    /TableCell> <
    TableCell > {
      row.component
    } < /TableCell> <
    TableCell >
    <
    Chip label = {
      row.decision_type
    }
    color = {
      color
    }
    size = "small" / >
    <
    /TableCell> <
    TableCell > {
      row.decision
    } < /TableCell> <
    TableCell align = "right" > {
      (row.confidence * 100).toFixed(1)
    } %
    <
    /TableCell> <
    /TableRow> <
    TableRow >
    <
    TableCell style = {
      {
        paddingBottom: 0,
        paddingTop: 0
      }
    }
    colSpan = {
      6
    } >
    <
    Collapse in = {
      open
    }
    timeout = "auto"
    unmountOnExit >
    <
    Box sx = {
      {
        margin: 1
      }
    } >
    <
    Typography variant = "h6"
    gutterBottom component = "div" >
    Details <
    /Typography> <
    Typography variant = "body2"
    gutterBottom >
    <
    strong > Audit ID: < /strong> {row.audit_id} <
    /Typography> <
    Typography variant = "body2"
    gutterBottom >
    <
    strong > Reasoning: < /strong> {row.reasoning || 'N/A'} <
    /Typography> <
    Typography variant = "body2"
    gutterBottom >
    <
    strong > Policies Applied: < /strong> {row.policies.join(', ') || 'None'} <
    /Typography> <
    strong > Input Data: < /strong> <
    pre style = {
      {
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-all',
        background: '#f5f5f5',
        padding: '8px',
        borderRadius: '4px'
      }
    } > {
      JSON.stringify(row.input_data, null, 2)
    } <
    /pre> <
    /Box> <
    /Collapse> <
    /TableCell> <
    /TableRow> <
    />
  )
}

export default function TransparencyLogPage() {
  const [logs, setLogs] = useState < AuditEntry[] > ([])
  const [loading, setLoading] = useState < boolean > (true)
  const [error, setError] = useState < string | null > (null)
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)

  useEffect(() => {
    async function fetchLogs() {
      try {
        setLoading(true)
        const response = await fetch('/api/governance/log')
        if (!response.ok) {
          throw new Error(`Failed to fetch logs: ${response.statusText}`)
        }
        const data = await response.json()
        if (data.error) {
          throw new Error(data.error)
        }
        // Sort by timestamp descending
        data.sort((a: AuditEntry, b: AuditEntry) => b.timestamp - a.timestamp)
        setLogs(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred')
      } finally {
        setLoading(false)
      }
    }
    fetchLogs()
  }, [])

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent < HTMLInputElement > ) => {
    setRowsPerPage(+event.target.value)
    setPage(0)
  }

  if (loading) {
    return ( <
      Container sx = {
        {
          py: 4
        }
      } >
      <
      Box sx = {
        {
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '80vh'
        }
      } >
      <
      CircularProgress / >
      <
      /Box> <
      /Container>
    )
  }

  if (error) {
    return ( <
      Container sx = {
        {
          py: 4
        }
      } >
      <
      Alert severity = "error" > Error loading audit log: {
        error
      } < /Alert> <
      /Container>
    )
  }

  return ( <
    Container maxWidth = "lg"
    sx = {
      {
        py: 4
      }
    } >
    <
    Typography variant = "h2"
    component = "h1"
    gutterBottom sx = {
      {
        fontWeight: 'thin',
        color: 'white'
      }
    } >
    Guardian System Transparency Log <
    /Typography> <
    Typography variant = "subtitle1"
    gutterBottom sx = {
      {
        color: 'rgba(255, 255, 255, 0.7)',
        mb: 4
      }
    } >
    A real - time, immutable log of decisions made by the LUKHAS Guardian system. <
    /Typography>

    <
    Card >
    <
    TableContainer component = {
      Paper
    } >
    <
    Table aria-label = "collapsible audit log table" >
    <
    TableHead >
    <
    TableRow >
    <
    TableCell / >
    <
    TableCell > Timestamp < /TableCell> <
    TableCell > Component < /TableCell> <
    TableCell > Type < /TableCell> <
    TableCell > Decision < /TableCell> <
    TableCell align = "right" > Confidence < /TableCell> <
    /TableRow> <
    /TableHead> <
    TableBody > {
      logs
      .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
      .map((row) => ( <
        Row key = {
          row.audit_id
        }
        row = {
          row
        }
        />
      ))
    } <
    /TableBody> <
    /Table> <
    /TableContainer> <
    TablePagination rowsPerPageOptions = {
      [10, 25, 100]
    }
    component = "div"
    count = {
      logs.length
    }
    rowsPerPage = {
      rowsPerPage
    }
    page = {
      page
    }
    onPageChange = {
      handleChangePage
    }
    onRowsPerPageChange = {
      handleChangeRowsPerPage
    }
    /> <
    /Card> <
    /Container>
  )
}
