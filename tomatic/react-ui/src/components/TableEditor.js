import * as React from 'react'
import PropTypes from 'prop-types'
import Box from '@mui/material/Box'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TablePagination from '@mui/material/TablePagination'
import TableRow from '@mui/material/TableRow'
import TableSortLabel from '@mui/material/TableSortLabel'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import Paper from '@mui/material/Paper'
import Checkbox from '@mui/material/Checkbox'
import IconButton from '@mui/material/IconButton'
import Tooltip from '@mui/material/Tooltip'
import FilterListIcon from '@mui/icons-material/FilterList'
import { visuallyHidden } from '@mui/utils'
import personData from '../persons.json'
import { contrast } from '../colorutils'
import EditIcon from '@mui/icons-material/Edit'
import EventBusyIcon from '@mui/icons-material/EventBusy'
import DeleteIcon from '@mui/icons-material/Delete'
import GroupAddIcon from '@mui/icons-material/GroupAdd'
import GroupRemoveIcon from '@mui/icons-material/GroupRemove'
import SearchIcon from '@mui/icons-material/Search'
import InputBase from '@mui/material/InputBase'
import { styled, alpha } from '@mui/material/styles'
/* eslint-enable */

const denseRowHeight = 33

function compileData() {
  const result = {}

  function joinAttribute(result, attribute) {
    Object.entries(personData[attribute + 's']).forEach(
      ([identifier, v], i) => {
        if (!result[identifier]) result[identifier] = { identifier: identifier }
        result[identifier][attribute] = v
      }
    )
  }
  function joinGroups(result) {
    Object.entries(personData.groups).forEach(([group, members], i) => {
      members.forEach((member) => {
        if (result[member] === undefined) {
          result[member] = { identifier: member }
        }
        if (result[member].groups === undefined) {
          result[member].groups = []
        }
        result[member].groups.push(group)
      })
    })
  }

  joinAttribute(result, 'name')
  joinAttribute(result, 'table')
  joinAttribute(result, 'extension')
  joinAttribute(result, 'color')
  joinAttribute(result, 'email')
  joinAttribute(result, 'erpuser')
  joinAttribute(result, 'load')
  joinGroups(result)

  return Object.entries(result).map(([identifier, v]) => {
    return v
  })
}

const rows = compileData()

function camelize(text) {
  text = text.toLowerCase()
  return text.charAt(0).toUpperCase() + text.slice(1)
}

const columns = [
  {
    id: 'identifier',
    numeric: false,
    disablePadding: true,
    label: 'Identificador',
  },
  {
    id: 'name',
    numeric: false,
    disablePadding: false,
    label: 'Nom / Color',
    view: (row) => {
      const bg = row.color || 'aaaaee'
      const fg = contrast(bg)
      return (
        <div
          style={{
            padding: '5px',
            backgroundColor: `#${bg}`,
            color: `${fg}`,
            border: `1pt solid ${fg}`,
            textAlign: 'center',
          }}
        >
          {row.name || camelize(row.identifier)}
        </div>
      )
    },
  },
  {
    id: 'extension',
    numeric: false,
    disablePadding: false,
    label: 'Extensió',
  },
  {
    id: 'email',
    numeric: true,
    disablePadding: false,
    label: 'Correu Electrònic',
  },
  {
    id: 'erpuser',
    numeric: false,
    disablePadding: false,
    label: 'Usuaria ERP',
  },
  {
    id: 'load',
    numeric: true,
    disablePadding: false,
    label: 'Torns',
  },
  {
    id: 'table',
    numeric: true,
    disablePadding: false,
    label: 'Taula',
  },
  {
    id: 'groups',
    numeric: true,
    disablePadding: false,
    label: 'Grups',
  },
]

const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  '&:hover': {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginLeft: 0,
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    marginLeft: theme.spacing(1),
    width: 'auto',
  },
}))

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}))

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: 'inherit',
  '& .MuiInputBase-input': {
    padding: theme.spacing(1, 1, 1, 0),
    // vertical padding + font size from searchIcon
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create('width'),
    width: '100%',
    [theme.breakpoints.up('sm')]: {
      width: '12ch',
      '&:focus': {
        width: '20ch',
      },
    },
  },
}))

function descendingComparator(a, b, orderBy) {
  function define(v) {
    return v === undefined ? -1 : v === null ? -1 : v
  }
  const avalue = define(a[orderBy])
  const bvalue = define(b[orderBy])
  if (bvalue < avalue) {
    return -1
  }
  if (bvalue > avalue) {
    return 1
  }
  return 0
}

function getComparator(order, orderBy) {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy)
}

// Since 2020 all major browsers ensure sort stability with Array.prototype.sort().
// stableSort() brings sort stability to non-modern browsers (notably IE11). If you
// only support modern browsers you can replace stableSort(exampleArray, exampleComparator)
// with exampleArray.slice().sort(exampleComparator)
function stableSort(array, comparator) {
  const stabilizedThis = array.map((el, index) => [el, index])
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0])
    if (order !== 0) {
      return order
    }
    return a[1] - b[1]
  })
  return stabilizedThis.map((el) => el[0])
}
function EnhancedTableHead(props) {
  const {
    onSelectAllClick,
    order,
    orderBy,
    numSelected,
    rowCount,
    onRequestSort,
  } = props
  const createSortHandler = (property) => (event) => {
    onRequestSort(event, property)
  }

  return (
    <TableHead>
      <TableRow>
        <TableCell padding="checkbox">
          <Checkbox
            color="primary"
            indeterminate={numSelected > 0 && numSelected < rowCount}
            checked={rowCount > 0 && numSelected === rowCount}
            onChange={onSelectAllClick}
            inputProps={{
              'aria-label': 'select all desserts',
            }}
          />
        </TableCell>
        {columns.map((column) => (
          <TableCell
            key={column.id}
            align={column.numeric ? 'right' : 'left'}
            padding={column.disablePadding ? 'none' : 'normal'}
            sortDirection={orderBy === column.id ? order : false}
          >
            <TableSortLabel
              active={orderBy === column.id}
              direction={orderBy === column.id ? order : 'asc'}
              onClick={createSortHandler(column.id)}
            >
              {column.label}
              {orderBy === column.id ? (
                <Box component="span" sx={visuallyHidden}>
                  {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                </Box>
              ) : null}
            </TableSortLabel>
          </TableCell>
        ))}
        <TableCell key={'action'} align={'right'} padding={'normal'}>
          {'Accions'}
        </TableCell>
      </TableRow>
    </TableHead>
  )
}

EnhancedTableHead.propTypes = {
  numSelected: PropTypes.number.isRequired,
  onRequestSort: PropTypes.func.isRequired,
  onSelectAllClick: PropTypes.func.isRequired,
  order: PropTypes.oneOf(['asc', 'desc']).isRequired,
  orderBy: PropTypes.string.isRequired,
  rowCount: PropTypes.number.isRequired,
}

function EnhancedTableToolbar(props) {
  const { numSelected, onSearchEdited, search, title } = props

  return (
    <Toolbar
      sx={{
        pl: { sm: 2 },
        pr: { xs: 1, sm: 1 },
        ...(numSelected > 0 && {
          bgcolor: (theme) =>
            alpha(
              theme.palette.primary.main,
              theme.palette.action.activatedOpacity
            ),
        }),
      }}
    >
      {numSelected > 0 ? (
        <Typography
          sx={{ flex: '1 1 100%' }}
          color="inherit"
          variant="subtitle1"
          component="div"
        >
          {`${numSelected} selected`}
        </Typography>
      ) : (
        <Box
          sx={{ flex: '1 1 100%' }}
          variant="h6"
          id="tableTitle"
          component="div"
        >
          {title}
        </Box>
      )}

      <Box sx={{ flex: '1 1 100%' }} variant="h6" id="Filter" component="div">
        <Search>
          <SearchIconWrapper>
            <SearchIcon />
          </SearchIconWrapper>
          <StyledInputBase
            placeholder={'Search…'}
            inputProps={{ 'aria-label': 'search' }}
            onChange={onSearchEdited}
            value={search}
          />
        </Search>
      </Box>
      {numSelected > 0 ? (
        <>
          <Tooltip title="Add to Group">
            <IconButton>
              <GroupAddIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Remove from Grou">
            <IconButton>
              <GroupRemoveIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Esborra">
            <IconButton>
              <DeleteIcon />
            </IconButton>
          </Tooltip>
        </>
      ) : (
        <Tooltip title="Filter list">
          <IconButton>
            <FilterListIcon />
          </IconButton>
        </Tooltip>
      )}
    </Toolbar>
  )
}

EnhancedTableToolbar.propTypes = {
  numSelected: PropTypes.number.isRequired,
}

export default function TableEditor(props) {
  const {title,defaultPageSize,pageSizes}=props;
  const [order, setOrder] = React.useState('asc')
  const [orderBy, setOrderBy] = React.useState('name')
  const [selected, setSelected] = React.useState([])
  const [page, setPage] = React.useState(0)
  const [rowsPerPage, setRowsPerPage] = React.useState(defaultPageSize)
  const [search, setSearch] = React.useState('')

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc'
    setOrder(isAsc ? 'desc' : 'asc')
    setOrderBy(property)
  }

  const handleSelectAllClick = (event) => {
    if (event.target.checked) {
      const newSelected = rows.map((n) => n.identifier)
      setSelected(newSelected)
      return
    }
    setSelected([])
  }

  const handleClick = (event, identifier) => {
    const selectedIndex = selected.indexOf(identifier)
    let newSelected = []

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, identifier)
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1))
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1))
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1)
      )
    }

    setSelected(newSelected)
  }

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const isSelected = (identifier) => selected.indexOf(identifier) !== -1

  // Avoid a layout jump when reaching the last page with empty rows.
  const emptyRows =
    page > 0 ? Math.max(0, (1 + page) * rowsPerPage - rows.length) : 0

  return (
    <Box sx={{ width: '100%' }}>
      <Paper sx={{ width: '100%', mb: 2 }}>
        <EnhancedTableToolbar
          title={title}
          numSelected={selected.length}
          search={search}
          onSearchEdited={(ev) => {
            setSearch(ev.target.value)
          }}
        />
        <TableContainer>
          <Table
            sx={{ minWidth: 750 }}
            aria-labelledby="tableTitle"
            size={'small'}
            stickyHeader
          >
            <EnhancedTableHead
              numSelected={selected.length}
              order={order}
              orderBy={orderBy}
              onSelectAllClick={handleSelectAllClick}
              onRequestSort={handleRequestSort}
              rowCount={rows.length}
            />
            <TableBody>
              {stableSort(rows, getComparator(order, orderBy))
                .filter((row) => {
                  return (
                    !search ||
                    (row.name && row.name.includes(search)) ||
                    (row.identifier && row.identifier.includes(search)) ||
                    (row.email && row.email.includes(search))
                  )
                })
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((row, index) => {
                  const isItemSelected = isSelected(row.identifier)
                  const labelId = `enhanced-table-checkbox-${index}`

                  return (
                    <TableRow
                      hover
                      onClick={(event) => handleClick(event, row.identifier)}
                      role="checkbox"
                      aria-checked={isItemSelected}
                      tabIndex={-1}
                      key={row.identifier}
                      selected={isItemSelected}
                    >
                      <TableCell padding="checkbox">
                        <Checkbox
                          color="primary"
                          checked={isItemSelected}
                          inputProps={{
                            'aria-labelledby': labelId,
                          }}
                        />
                      </TableCell>
                      <TableCell
                        component="th"
                        id={labelId}
                        scope="row"
                        padding="none"
                      >
                        {row.identifier}
                      </TableCell>
                      {columns
                        .filter((x) => x.id !== 'identifier')
                        .map((column) => {
                          return (
                            <TableCell
                              key={row.identifier + '_' + column.id}
                              align="right"
                            >
                              {column.view
                                ? column.view(row)
                                : row === undefined
                                ? '-'
                                : row === null
                                ? '-'
                                : row[column.id]}
                            </TableCell>
                          )
                        })}
                      <TableCell>
                        <Tooltip title="Edita">
                          <IconButton
                            onClick={(ev) => {
                              ev.stopPropagation()
                            }}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Indisponibilitats">
                          <IconButton
                            onClick={(ev) => {
                              ev.stopPropagation()
                            }}
                          >
                            <EventBusyIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  )
                })}
              {emptyRows > 0 && (
                <TableRow
                  style={{
                    height: denseRowHeight * emptyRows,
                  }}
                >
                  <TableCell colSpan={6} />
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={pageSizes}
          component="div"
          count={rows.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  )
}
