create table liga_mx_21_23 as 
with equipos as (
    select distinct team_id,
                    upper(case
                        when team_name='Atlético San Luis' then 'Atletico San Luis'
                        when team_name='León' then 'Leon'
                        else team_name end) as team_name
    from dim_teams
    ),
    estadios as (
        select distinct venue_id,
                        upper(case
                            when venue_name='Estadio León' then 'Estadio Leon'
                            when venue_name='Estadio Olímpico de Universitario' then 'Estadio Olímpico Universitario'
                            when venue_name='Estadio León' then 'Estadio Leon'
                            else venue_name
                            end
                        ) as venue_name
        from dim_venues
    ),
    base as (select m.*,
           upper(v.venue_name) as venue_name,
           upper(t1.team_name) as home_name_team,
           upper(t2.team_name) as away_name_team
    from fact_matches m
        left join dim_venues v on m.venue_id=v.venue_id
        left join equipos t1 on m.home_team_id=t1.team_id
        left join equipos t2 on m.away_team_id=t2.team_id
    ),
    tabla_semifinal as (
        select distinct 
            match_id as id_partido,
           date(leftstr("fixture.date",10)) as fecha_partido,
           substr("fixture.date",12,5) as horario,
           venue_name as nombre_estadio,
           case
               when "league.round" like '%Apertura%' then 'Apertura '
               else 'Clausura '
               end as torneo,
           case
               when "league.round" like '%Play%' then 'Repechaje'
               when "league.round" like '%Rec%' then 'Repechaje'
               when "league.round" like '%Qua%' then 'Cuartos de Final'
               when "league.round" like '%Sem%' then 'Semifinal'
               when "league.round" like '%Fi%' then 'Final'
               else replace(rightstr("league.round",2),' ','')
               end as jornada,
           home_name_team as equipo_local,
           away_name_team as equipo_visitante,
           home_goals as goles_local,
           away_goals as goles_visitante,
           case
               when home_goals>away_goals then 'LOCAL'
               when home_goals<away_goals then 'VISITANTE'
               else 'EMPATE' end as resultado
        from base
    ),
    tabla_final as (
        select distinct
            id_partido,
            fecha_partido,
            horario,
            case
                when equipo_local='NECAXA' then 'ESTADIO VICTORIA'
                when nombre_estadio='ESTADIO CORREGIDORA' then 'ESTADIO LA CORREGIDORA'
                WHEN nombre_estadio='ESTADIO CORONA' THEN 'ESTADIO NUEVO CORONA'
                when nombre_estadio is null then
                    case
                        when equipo_local='U.N.A.M. - PUMAS' then 'ESTADIO OLíMPICO DE UNIVERSITARIO'
                        when equipo_local='LEON' then 'ESTADIO DE LEON'
                        when equipo_local='TIGRES UANL' then 'ESTADIO UNIVERSITARIO DE NUEVO LEóN'
                        end
                    else nombre_estadio end as nombre_estadio,
            torneo,
            jornada,
            equipo_local,
            equipo_visitante,
            goles_local,
            goles_visitante,
            resultado
        from tabla_semifinal
    )
select *
from tabla_final
ORDER BY fecha_partido, jornada, horario, id_partido